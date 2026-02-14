#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
from collections import deque

import wurb_core
import wurb_utils


class RecWorker(object):
    """ """

    def __init__(self, config=None, logger=None, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logger
        if self.config == None:
            self.config = {}
        if self.logger == None:
            self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """
        self.source_worker = None
        self.process_worker = None
        self.target_worker = None
        self.from_source_queue = None
        self.to_target_queue = None

    def configure(self):
        """ """
        self.queue_max_size = 100
        self.rec_timeout_before_restart_s = 30
        self.max_adc_time_diff_s = 60
        self.restart_activated = False
        self.connected_device_name = ""
        self.connected_device_index = ""
        self.connected_input_channels = ""
        self.config_input_channels = ""
        self.connected_sampling_freq_hz = ""

    def start_recording(self):
        """ """
        try:
            device_info = wurb_core.rec_devices.get_capture_device_info()
            device_name = device_info.get("device_name", "")
            # Create queues.
            if self.from_source_queue == None:
                self.from_source_queue = asyncio.Queue(maxsize=self.queue_max_size)
                if device_name == "Pettersson M500 (500kHz)":
                    wurb_core.m500.add_out_queue(self.from_source_queue)
                else:
                    wurb_core.audio_capture.add_out_queue(self.from_source_queue)
            if self.to_target_queue == None:
                self.to_target_queue = asyncio.Queue(maxsize=self.queue_max_size)
            # # Clear queues.
            # self.remove_items_from_queue(self.from_source_queue)
            # self.remove_items_from_queue(self.to_target_queue)
            # Sound capture task.
            if self.source_worker == None:
                # Clear queue.
                self.remove_items_from_queue(self.from_source_queue)
                self.source_worker = asyncio.create_task(
                    self.rec_source_worker(), name="RecWorker source task"
                )
                self.logger.debug("REC SOURCE STARTED.")
            # Sound process task.
            if self.process_worker == None:
                # Clear queue.
                self.remove_items_from_queue(self.to_target_queue)
                self.process_worker = asyncio.create_task(
                    self.rec_process_worker(), name="RecWorker process task"
                )
                self.logger.debug("REC PROCESS STARTED.")
            # Sound target task.
            if self.target_worker == None:
                self.target_worker = asyncio.create_task(
                    self.rec_target_worker(), name="RecWorker target task"
                )
                self.logger.debug("REC TARGET STARTED.")
        except Exception as e:
            self.logger.debug("RecWorker, start_recording: " + str(e))

    async def stop_recording(self):
        """ """
        try:
            device_info = wurb_core.rec_devices.get_capture_device_info()
            device_name = device_info.get("device_name", "")
            # Sound capture task.
            if self.source_worker != None:
                if device_name == "Pettersson M500 (500kHz)":
                    await wurb_core.m500.stop()
                else:
                    await wurb_core.audio_capture.stop()
                self.source_worker.cancel()
                self.source_worker = None
                self.logger.debug("REC SOURCE CANCELED.")
            # Sound process task.
            if self.process_worker != None:
                self.process_worker.cancel()
                self.process_worker = None
                self.logger.debug("REC PROCESS CANCELED.")
            # Sound target task.
            if self.target_worker != None:
                self.target_worker.cancel()
                self.target_worker = None
                self.logger.debug("REC TARGET CANCELED.")
            # Clear queues.
            self.remove_items_from_queue(self.from_source_queue)
            self.remove_items_from_queue(self.to_target_queue)
        except Exception as e:
            self.logger.debug("RecWorker, stop_recording: " + str(e))

    async def rec_source_worker(self):
        """ """
        try:
            # Check available microphones.
            device_info = wurb_core.rec_devices.get_capture_device_info()
            self.connected_device_name = device_info.get("device_name", "")
            self.connected_device_index = device_info.get("device_index", "")
            self.connected_input_channels = device_info.get("input_channels", "")
            self.connected_config_channels = device_info.get("config_channels", "")
            self.connected_sampling_freq_hz = device_info.get("sampling_freq_hz", "")
            if self.connected_device_index in [None, ""]:
                self.logger.debug("NO MIC.")
                return

            # Set up microphone.
            # Process buffer 0.25 sec.
            process_buffer_size = int(float(self.connected_sampling_freq_hz) / 4)
            # frames_per_buffer = int(float(self.connected_sampling_freq_hz) / 8)
            frames_per_buffer = int(1024.0 * 4)
            if self.connected_device_name == "Pettersson M500 (500kHz)":
                wurb_core.m500.setup(
                    device_index=self.connected_device_index,
                    device_name=self.connected_device_name,
                    channels=self.connected_input_channels,
                    config_channels=self.connected_config_channels,
                    sampling_freq_hz=int(self.connected_sampling_freq_hz),
                    frames_per_buffer=frames_per_buffer,
                    buffer_size=process_buffer_size,
                )
            else:
                wurb_core.audio_capture.setup(
                    device_index=self.connected_device_index,
                    device_name=self.connected_device_name,
                    channels=self.connected_input_channels,
                    config_channels=self.connected_config_channels,
                    sampling_freq_hz=int(self.connected_sampling_freq_hz),
                    frames_per_buffer=frames_per_buffer,
                    buffer_size=process_buffer_size,
                )

            if self.connected_device_name == "Pettersson M500 (500kHz)":
                await wurb_core.m500.start()
            else:
                await wurb_core.audio_capture.start()                
            self.logger.debug("RecWorker - Sound capture started.")
        except Exception as e:
            message = "RecWorker - rec_source_worker. Exception: " + str(e)
            self.logger.debug(message)
            return

    async def rec_process_worker(self):
        """ """
        self.restart_activated = False
        try:
            # Get rec length from settings.
            self.rec_length_s = int(wurb_core.wurb_settings.get_setting("recLengthS"))
            #
            self.process_deque = deque()  # Double ended queue.
            self.process_deque.clear()
            # self.process_deque_length = self.rec_length_s * 2
            self.process_deque_length = self.rec_length_s * 4
            # self.detection_counter_max = self.process_deque_length - 2  # 1.0 s before.
            self.detection_counter_max = self.process_deque_length - 4  # 1.0 s before.
            #
            first_sound_detected = False
            sound_detected = False
            sound_detected_counter = 0

            sound_detector = wurb_core.sound_detection.get_detection()

            max_peak_hz = None
            max_peak_dbfs = None

            while True:
                try:
                    try:
                        try:
                            item = await asyncio.wait_for(
                                self.from_source_queue.get(),
                                timeout=self.rec_timeout_before_restart_s,
                            )
                        except asyncio.TimeoutError:
                            # Check if restart already is requested.
                            if self.restart_activated:
                                return
                            # Logging.
                            message = (
                                "Lost connection with the microphone. Rec. restarted."
                            )
                            self.logger.warning(message)
                            # Check connected microphones.
                            wurb_core.rec_devices.clear()
                            # PyAudio has to be terminated and reloaded.
                            # wurb_core.audio.terminate()
                            # wurb_core.audio = wurb_core.pyaudio.PyAudio()


                            # wurb_core.audio_capture = wurb_utils.AudioCapture(wurb_core.audio, logger_name=wurb_core.logger_name)
                            # wurb_core.audio_playback = wurb_utils.AudioPlayback(wurb_core.audio, logger_name=wurb_core.logger_name)


                            wurb_core.rec_devices.get_capture_device_info()
                            # Restart recording.
                            self.restart_activated = True
                            loop = asyncio.get_event_loop()
                            asyncio.run_coroutine_threadsafe(
                                wurb_core.rec_manager.restart_rec(),
                                loop,
                            )
                            self.remove_items_from_queue(self.from_source_queue)
                            await self.from_source_queue.put(False)  # Flush.
                            return
                        #
                        try:
                            # print("REC PROCESS: ", item["adc_time"], item["data"][:5])
                            if item == None:
                                first_sound_detected == False
                                sound_detected_counter = 0
                                self.process_deque.clear()
                                await self.to_target_queue.put(None)  # Terminate.
                                break
                            elif item == False:
                                first_sound_detected == False
                                sound_detected_counter = 0
                                self.process_deque.clear()
                                self.remove_items_from_queue(self.to_target_queue)
                                await self.to_target_queue.put(False)  # Flush.
                            else:
                                # Compare real time and stream time.
                                adc_time = item["adc_time"]
                                detector_time = item["detector_time"]
                                # Restart if it differ too much.
                                if (
                                    abs(adc_time - detector_time)
                                    > self.max_adc_time_diff_s
                                ):
                                    # Check if restart already is requested.
                                    if self.restart_activated:
                                        return
                                    # Logging.
                                    message = "Warning: Time diff. detected. Rec. will be restarted."
                                    self.logger.warning(message)
                                    message = (
                                        "Warning: Time diff. ADC: "
                                        + str(adc_time)
                                        + " detector: "
                                        + str(detector_time)
                                        + "."
                                    )
                                    self.logger.debug(message)
                                    # Restart recording.
                                    self.restart_activated = True
                                    loop = asyncio.get_event_loop()
                                    asyncio.run_coroutine_threadsafe(
                                        wurb_core.rec_manager.restart_rec(),
                                        loop,
                                    )
                                    self.remove_items_from_queue(self.from_source_queue)
                                    await self.from_source_queue.put(False)  # Flush.
                                    return

                                # Store in list.
                                new_item = {}
                                new_item["status"] = "data-Counter-" + str(
                                    sound_detected_counter
                                )
                                new_item["adc_time"] = item["adc_time"]
                                new_item["data"] = item["data"]

                                self.process_deque.append(new_item)
                                # Remove oldest items if the list is too long.
                                while (
                                    len(self.process_deque) > self.process_deque_length
                                ):
                                    self.process_deque.popleft()

                                # Check for sound.
                                detection_result = sound_detector.check_for_sound(
                                    (item["adc_time"], item["data"])
                                )
                                (
                                    sound_detected,
                                    detected_peak_hz,
                                    detected_peak_dbfs,
                                ) = detection_result

                                if (not first_sound_detected) and sound_detected:
                                    first_sound_detected = True
                                    sound_detected_counter = 0
                                    max_peak_hz = detected_peak_hz
                                    max_peak_dbfs = detected_peak_dbfs
                                    # Log first detected sound.
                                    if detected_peak_dbfs and detected_peak_dbfs:
                                        # Logging.
                                        message = (
                                            "Sound peak: "
                                            + str(round(detected_peak_hz / 1000.0, 1))
                                            + " kHz / "
                                            + str(round(detected_peak_dbfs, 1))
                                            + " dBFS."
                                        )
                                        self.logger.info(message)

                                # Accumulate in file queue.
                                if first_sound_detected == True:
                                    sound_detected_counter += 1
                                    if detected_peak_dbfs and max_peak_dbfs:
                                        if detected_peak_dbfs > max_peak_dbfs:
                                            max_peak_hz = detected_peak_hz
                                            max_peak_dbfs = detected_peak_dbfs
                                    if (
                                        sound_detected_counter
                                        >= self.detection_counter_max
                                    ) and (
                                        len(self.process_deque)
                                        >= self.process_deque_length
                                    ):
                                        first_sound_detected = False
                                        sound_detected_counter = 0
                                        # Send to target.
                                        for index in range(
                                            0, self.process_deque_length
                                        ):
                                            to_file_item = self.process_deque.popleft()
                                            #
                                            if index == 0:
                                                to_file_item["status"] = "new_file"
                                                to_file_item["peak_hz"] = max_peak_hz
                                                to_file_item[
                                                    "peak_dbfs"
                                                ] = max_peak_dbfs
                                            if index == (self.process_deque_length - 1):
                                                to_file_item["status"] = "close_file"
                                            #
                                            if not self.to_target_queue.full():
                                                await self.to_target_queue.put(
                                                    to_file_item
                                                )
                        finally:
                            self.from_source_queue.task_done()
                            await asyncio.sleep(0)

                    except asyncio.QueueFull:
                        self.logger.debug("RecWorker - Queue full, items removed.")
                        self.remove_items_from_queue(self.to_target_queue)
                        self.process_deque.clear()
                        await self.to_target_queue.put(False)  # Flush.
                except asyncio.CancelledError:
                    self.logger.debug("RecWorker - Sound process was cancelled.")
                    break
                except Exception as e:
                    message = "RecWorker - rec_process_worker(1). Exception: " + str(e)
                    self.logger.debug(message)

                await asyncio.sleep(0)
            # While end.

        except Exception as e:
            message = "RecWorker - rec_process_worker(2). Exception: " + str(e)
            self.logger.debug(message)
        finally:
            self.logger.debug("RecWorker - Sound process ended.")

    async def rec_target_worker(self):
        """Worker for sound targets. Mainly files or streams."""
        wave_file_writer = None
        try:
            while True:
                try:
                    item = await self.to_target_queue.get()
                    try:
                        if item == None:
                            # Terminated by process.
                            break
                        elif item == False:
                            self.remove_items_from_queue(self.to_target_queue)
                            if wave_file_writer:
                                old_file_writer = wave_file_writer
                                wave_file_writer = None
                                old_file_writer.close()
                        else:
                            # New.
                            if item["status"] == "new_file":
                                if wave_file_writer:
                                    old_file_writer = wave_file_writer
                                    wave_file_writer = None
                                    old_file_writer.close()
                                # Create new file writer.
                                peak_hz = item.get("peak_hz", None)
                                peak_dbfs = item.get("peak_dbfs", None)
                                wave_file_writer = wurb_core.RecFileWriter()
                                wave_file_writer.prepare(
                                    self.connected_device_name,
                                    self.connected_sampling_freq_hz,
                                    item["adc_time"],
                                    peak_hz,
                                    peak_dbfs,
                                )
                                wave_file_writer.open()
                            # Data.
                            if wave_file_writer:
                                data_array = item["data"]
                                wave_file_writer.write(data_array)
                            # File.
                            if item["status"] == "close_file":
                                if wave_file_writer:
                                    old_file_writer = wave_file_writer
                                    wave_file_writer = None
                                    old_file_writer.close()
                    finally:
                        self.to_target_queue.task_done()
                        await asyncio.sleep(0)

                except asyncio.CancelledError:
                    self.logger.debug("Sound target was cancelled.")
                    break
                except Exception as e:
                    message = "RecWorker - rec_target_worker(1): " + str(e)
                    self.logger.debug(message)

                await asyncio.sleep(0)

        except Exception as e:
            message = "RecWorker - rec_target_worker(2). Exception: " + str(e)
            self.logger.debug(message)
        finally:
            self.logger.debug("RecWorker - Sound target ended.")

    def remove_items_from_queue(self, queue):
        """Helper method."""
        try:
            if queue:
                while True:
                    try:
                        queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        return
        except Exception as e:
            message = "RecWorker - remove_items_from_queue. Exception: " + str(e)
            self.logger.debug(message)
