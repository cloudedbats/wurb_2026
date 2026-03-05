#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import numpy
import time
import sounddevice


class AudioCapture:
    """ """

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.clear()

    def clear(self):
        self.device_index = None
        self.device_name = ""
        self.channels = None
        self.config_channels = None
        self.sampling_freq_hz = None
        self.frames_per_buffer = None
        self.buffer_size = None
        #
        self.out_queue_list = []
        self.main_loop = None
        self.capture_executor = None
        self.capture_is_running = False
        self.capture_is_active = False

    def is_capture_running(self):
        """ """
        return self.capture_is_running

    def get_selected_capture_device(self):
        """ """
        info_dict = {}
        info_dict["device_index"] = self.device_index
        info_dict["device_name"] = self.device_name
        info_dict["input_channels"] = self.channels
        info_dict["config_channels"] = self.config_channels
        info_dict["sampling_freq_hz"] = self.sampling_freq_hz
        return info_dict

    def refresh_device_list(device=None):
        """Needed for plug-and-play."""
        sounddevice._terminate()
        sounddevice._initialize()

    def get_capture_devices(self):
        """ """
        # Do not check if running.
        if self.capture_is_active == True:
            info_dict = self.get_selected_capture_device()
            return [info_dict]
        #
        self.refresh_device_list()
        #
        devices = []
        try:
            device_list = sounddevice.query_devices(device=None)
            for device in device_list:
                input_channels = device.get("max_input_channels", 0)
                if input_channels > 0:
                    info_dict = {}
                    info_dict["device_name"] = device.get("name", "")
                    info_dict["input_channels"] = input_channels
                    info_dict["device_index"] = device.get("index", -1)
                    info_dict["sampling_freq_hz"] = device.get("default_samplerate", -1)
                    devices.append(info_dict)
        except Exception as e:
            self.logger.debug("AudioCapture - get_capture_devices: " + str(e))
        return devices

    def setup(
        self,
        device_index,
        device_name,
        channels,
        config_channels,
        sampling_freq_hz,
        frames_per_buffer,
        buffer_size,
    ):
        """ """
        self.device_index = device_index
        self.device_name = device_name
        self.channels = channels
        self.config_channels = config_channels
        self.sampling_freq_hz = sampling_freq_hz
        self.frames_per_buffer = frames_per_buffer
        self.buffer_size = buffer_size

    def add_out_queue(self, out_queue):
        """ """
        self.out_queue_list.append(out_queue)

    async def start(self):
        """ """
        try:
            if self.capture_is_running == True:
                self.logger.debug(
                    "AudioCapture - Start: Capture is running, waiting 2 sec... "
                )
                await asyncio.sleep(2.0)
                if self.capture_is_running == True:
                    self.logger.debug(
                        "AudioCapture - Start: Capture is still running, will be stopped... "
                    )
                    await self.stop()

            # Use executor for the IO-blocking part.
            self.main_loop = asyncio.get_event_loop()
            # self.capture_executor = self.main_loop.run_in_executor(
            #     None, self.run_capture
            # )
            self.capture_executor = asyncio.create_task(
                self.run_capture(), name="Sound capture task"
            )
        except Exception as e:
            message = "AlsaAudioPlayback - start. Exception: " + str(e)
            self.logger.debug(message)

    async def stop(self):
        """ """
        try:
            self.capture_is_active = False
            if self.capture_executor != None:
                self.capture_executor.cancel()
                self.capture_executor = None
        except Exception as e:
            message = "AlsaAudioPlayback - stop. Exception: " + str(e)
            self.logger.debug(message)

    async def run_capture(self):
        """ """
        stream = None
        self.capture_is_active = True
        try:
            self.logger.debug("AudioCapture - Sound capture started.")

            # input_stream_queue = asyncio.Queue()
            input_stream_list = []
            loop = asyncio.get_event_loop()

            def callback(in_data, frame_count, time_info, status):
                # Callback from sounddevice.InputStream.
                in_buffer = in_data[:, 0].copy()
                callback_list = [
                    in_buffer,
                    frame_count,
                    time_info,
                    status,
                ]
                input_stream_list.append(callback_list)

            stream = sounddevice.InputStream(
                callback=callback,
                blocksize=self.frames_per_buffer,
                samplerate=self.sampling_freq_hz,
                channels=self.channels,
                device=self.device_index,
                dtype="int16",
            )

            self.capture_is_running = True
            # Time related.
            calculated_time_s = time.time()
            time_increment_s = self.buffer_size / self.sampling_freq_hz
            # Empty numpy buffer.
            in_buffer_int16 = numpy.array([], dtype=numpy.int16)
            #
            await asyncio.sleep(0)
            #
            with stream:
                while self.capture_is_active:
                    
                    if len(input_stream_list) <= 0:
                        await asyncio.sleep(0.01)
                        continue

                    callback_list = input_stream_list.pop(0)

                    in_buffer = callback_list[0]
                    frame_count = callback_list[1]
                    time_info = callback_list[2]
                    status = callback_list[3]

                    if status:
                        self.logger.debug("AudioCapture - Status: " + str(status))

                    if len(input_stream_list) > 5:
                        print("CAPTURE: Frame count: ", frame_count, " List length: ", len(input_stream_list))
                    # print("CAPTURE: AdcTime: ", time_info.inputBufferAdcTime)
                    # print("CAPTURE: currentTime: ", time_info.currentTime)
                    # print("CAPTURE: time.time(): ", time.time())

                    # # Convert stereo to mono by using either left or right channel.
                    # if self.config_channels in ["MONO-LEFT", "MONO-RIGHT"]:
                    #     if self.config_channels.upper() == "MONO-LEFT":
                    #         in_data_int16 = callback_dict.in_data[0::2].copy()
                    #     if self.config_channels.upper() == "MONO-RIGHT":
                    #         in_data_int16 = callback_dict.in_data[1::2].copy()
                    # else:
                    #     in_data_int16 = callback_dict.in_data[:, 0]

                    # # Concatenate
                    in_buffer_int16 = numpy.concatenate(
                        (in_buffer_int16, in_buffer)
                    )
                    while len(in_buffer_int16) >= self.buffer_size:
                        # Copy "buffer_size" part and save remaining part.
                        data_int16 = in_buffer_int16[0 : self.buffer_size]
                        in_buffer_int16 = in_buffer_int16[self.buffer_size :]

                        # Put data on queues in the queue list.
                        for data_queue in self.out_queue_list:
                            # Time rounded to half sec.
                            calculated_time_s += time_increment_s
                            device_time = int((calculated_time_s) * 2) / 2
                            # Used to detect time drift.
                            detector_time = time.time()
                            # Copy data.
                            data_int16_copy = data_int16.copy()
                            # Put together.
                            data_dict = {
                                "status": "data",
                                "adc_time": device_time,
                                "detector_time": detector_time,
                                "data": data_int16_copy,
                            }
                            try:
                                if not data_queue.full():
                                    self.main_loop.call_soon_threadsafe(
                                        data_queue.put_nowait, data_dict
                                    )
                                else:
                                    self.logger.debug("AudioCapture - Queue full.")
                            #
                            except Exception as e:
                                message = (
                                    "AudioCapture - Failed to put captured sound on queue: "
                                    + str(e)
                                )
                                self.logger.error(message)
                                if not self.main_loop.is_running():
                                    # Terminate.
                                    self.capture_is_active = False
                                    break
                    await asyncio.sleep(0)
                #
                await asyncio.sleep(0)
        #
        except asyncio.CancelledError:
            self.logger.debug("AudioCapture - Was cancelled.")
        except Exception as e:
            message = "AudioCapture - run_capture. Exception: " + str(e)
            self.logger.debug(message)
        finally:
            self.logger.debug("AudioCapture - Capture ended.")
            self.capture_is_active = False
            # if stream:
            #     stream.close()
            self.capture_is_running = False

    # async def run_capture(self):
    #     """ """
    #     stream = None
    #     self.capture_is_active = True
    #     try:
    #         self.logger.debug("AudioCapture - Sound capture started.")

    #         input_stream_queue = asyncio.Queue()
    #         loop = asyncio.get_event_loop()

    #         def callback(in_data, frame_count, time_info, status):
    #             loop.call_soon_threadsafe(
    #                 input_stream_queue.put_nowait,
    #                 (
    #                     in_data.copy(),
    #                     frame_count,
    #                     time_info,
    #                     status,
    #                 ),
    #             )

    #         stream = sounddevice.InputStream(
    #             callback=callback,
    #             blocksize=self.frames_per_buffer,
    #             samplerate=self.sampling_freq_hz,
    #             channels=self.channels,
    #             device=self.device_index,
    #             dtype="int16",
    #         )

    #         self.capture_is_running = True
    #         # Time related.
    #         calculated_time_s = time.time()
    #         time_increment_s = self.buffer_size / self.sampling_freq_hz
    #         # Empty numpy buffer.
    #         in_buffer_int16 = numpy.array([], dtype=numpy.int16)
    #         #
    #         await asyncio.sleep(0)
    #         #
    #         with stream:
    #             while self.capture_is_active:

    #                 in_data, frame_count, time_info, status = (
    #                     await input_stream_queue.get()
    #                 )

    #                 if status:
    #                     self.logger.debug("AudioCapture - Status: " + str(status))

    #                 # print("CAPTURE: Frame count: ", frame_count)
    #                 print("CAPTURE: AdcTime: ", time_info.inputBufferAdcTime)
    #                 print("CAPTURE: currentTime: ", time_info.currentTime)
    #                 print("CAPTURE: time.time(): ", time.time())

    #                 # Convert stereo to mono by using either left or right channel.
    #                 if self.config_channels in ["MONO-LEFT", "MONO-RIGHT"]:
    #                     if self.config_channels.upper() == "MONO-LEFT":
    #                         in_data_int16 = in_data[0::2].copy()
    #                     if self.config_channels.upper() == "MONO-RIGHT":
    #                         in_data_int16 = in_data[1::2].copy()
    #                 else:
    #                     in_data_int16 = in_data[:, 0]
    #                 # Concatenate
    #                 in_buffer_int16 = numpy.concatenate(
    #                     (in_buffer_int16, in_data_int16)
    #                 )
    #                 while len(in_buffer_int16) >= self.buffer_size:
    #                     # Copy "buffer_size" part and save remaining part.
    #                     data_int16 = in_buffer_int16[0 : self.buffer_size]
    #                     in_buffer_int16 = in_buffer_int16[self.buffer_size :]

    #                     # Put data on queues in the queue list.
    #                     for data_queue in self.out_queue_list:
    #                         # Time rounded to half sec.
    #                         calculated_time_s += time_increment_s
    #                         device_time = int((calculated_time_s) * 2) / 2
    #                         # Used to detect time drift.
    #                         detector_time = time.time()
    #                         # Copy data.
    #                         data_int16_copy = data_int16.copy()
    #                         # Put together.
    #                         data_dict = {
    #                             "status": "data",
    #                             "adc_time": device_time,
    #                             "detector_time": detector_time,
    #                             "data": data_int16_copy,
    #                         }
    #                         try:
    #                             if not data_queue.full():
    #                                 self.main_loop.call_soon_threadsafe(
    #                                     data_queue.put_nowait, data_dict
    #                                 )
    #                             else:
    #                                 self.logger.debug("AudioCapture - Queue full.")
    #                         #
    #                         except Exception as e:
    #                             message = (
    #                                 "AudioCapture - Failed to put captured sound on queue: "
    #                                 + str(e)
    #                             )
    #                             self.logger.error(message)
    #                             if not self.main_loop.is_running():
    #                                 # Terminate.
    #                                 self.capture_is_active = False
    #                                 break
    #                 #
    #                 await asyncio.sleep(0)
    #     #
    #     except asyncio.CancelledError:
    #         self.logger.debug("AudioCapture - Was cancelled.")
    #     except Exception as e:
    #         message = "AudioCapture - run_capture. Exception: " + str(e)
    #         self.logger.debug(message)
    #     finally:
    #         self.logger.debug("AudioCapture - Capture ended.")
    #         self.capture_is_active = False
    #         # if stream:
    #         #     stream.close()
    #         self.capture_is_running = False
