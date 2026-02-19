#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import serial.tools.list_ports

import wurb_core
import wurb_utils


class RecManager(object):
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
        self.control_loop = None
        self.last_used_rec_mode = ""
        self.manual_trigger_activated = False
        self.status_info_text = ""
        self.status_info_text_old = ""
        #
        self.rec_event = None
        self.notification_event = None

    def configure(self):
        """ """
        self.control_loop_interval_s = self.config.get(
            "rec_manager.control_loop_interval_s", 10
        )

    def startup(self):
        """ """
        # Log connected microphones at startup.
        available_devices = wurb_core.audio_capture.get_capture_devices()
        try:
            self.logger.debug("Connected microphones at startup:")
            for device_dict in available_devices:
                device_full_name = device_dict["device_name"]
                sampling_freq_hz = device_dict["sampling_freq_hz"]
                freq_list = device_dict.get("freq_list", sampling_freq_hz)
                input_channels = device_dict["input_channels"]
                channels = "MONO"
                if input_channels == 2:
                    channels = "STEREO"
                message = (
                    "- "
                    + device_full_name
                    + "   "
                    + channels
                    + " at "
                    # + str(sampling_freq_hz)
                    + str(freq_list)
                    + " Hz "
                )
                self.logger.debug(message)
            # Also check Pettersson M500.
            if wurb_core.m500.is_m500_available():
                message = (
                    "- "
                    + wurb_core.m500.device_name
                    + "   "
                    + "MONO"
                    + " at "
                    + str(wurb_core.m500.sampling_freq_hz)
                    + " Hz "
                )
                self.logger.debug(message)
        except Exception as e:
            message = "RecManager - startup. Exception: " + str(e)
            self.logger.debug(message)

        # Log connected serial devices (like GPS and LoRa) at startup.
        try:
            comports = serial.tools.list_ports.comports()
            if len(comports) > 0:
                self.logger.debug("Connected serial devices at startup:")
                for info in serial.tools.list_ports.comports():
                    message = "- Device: " + info.device + " HWID: " + info.hwid
                    self.logger.debug(message)
            else:
                self.logger.debug("No serial devices are connected at startup.")
        except Exception as e:
            message = "RecManager - startup. Exception: " + str(e)
            self.logger.debug(message)
        # Load microphone that match config.
        wurb_core.rec_devices.get_capture_device_info()
        # Activate GPS.
        wurb_core.gps_reader.startup()
        # Activte REcManager.
        self.control_loop = asyncio.create_task(
            self.rec_control_loop(), name="RecManager control task"
        )

    async def shutdown(self):
        """ """
        await wurb_core.rec_worker.stop_recording()
        wurb_core.gps_reader.shutdown()
        if self.rec_event:
            self.rec_event.set()
        if self.notification_event:
            self.notification_event.set()
        if self.control_loop != None:
            self.control_loop.cancel()

    async def rec_control_loop(self):
        """ """
        try:
            self.manual_trigger_activated = False
            await self.check_status()

            settings_event = wurb_core.wurb_settings.get_settings_event()
            location_event = wurb_core.wurb_settings.get_location_event()
            latlong_event = wurb_core.gps_reader.get_latlong_event()
            while True:
                task_1 = asyncio.create_task(
                    asyncio.sleep(self.control_loop_interval_s), name="rec-sleep"
                )
                task_2 = asyncio.create_task(
                    settings_event.wait(), name="rec-settings-event"
                )
                task_3 = asyncio.create_task(
                    location_event.wait(), name="rec-location-event"
                )
                task_4 = asyncio.create_task(
                    latlong_event.wait(), name="rec-latlong-event"
                )
                events = [
                    task_1,
                    task_2,
                    task_3,
                    task_4,
                ]
                done, pending = await asyncio.wait(
                    events, return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    task.cancel()
                    # print("Done REC: ", task.get_name())
                for task in pending:
                    task.cancel()

                if settings_event.is_set():
                    settings_event = wurb_core.wurb_settings.get_settings_event()
                    # Settings changed, rec restart needed.
                    await self.restart_rec()
                if location_event.is_set():
                    location_event = wurb_core.wurb_settings.get_location_event()
                if latlong_event.is_set():
                    latitude, longitude = wurb_core.gps_reader.get_latitude_longitude()
                    # print("Lat-long: ", latitude, "   ", longitude)
                    await wurb_core.wurb_settings.save_latlong(latitude, longitude)
                    latlong_event = wurb_core.gps_reader.get_latlong_event()

                await self.check_status()

        except asyncio.CancelledError:
            self.logger.debug("Rec control loop was cancelled.")
        except Exception as e:
            message = "RecManager - rec_control_loop. Exception: " + str(e)
            self.logger.debug(message)
        finally:
            message = "Rec control loop terminated."
            self.logger.debug(message)

    async def check_status(self):
        """ """
        try:
            is_rec_mode_on = False
            is_scheduler_used = False
            is_rec_to_be_activated = False
            self.status_info_text = ""

            # Check rec mode and scheduler.
            rec_mode = wurb_core.wurb_settings.get_setting("recMode")

            if rec_mode != self.last_used_rec_mode:
                self.last_used_rec_mode = rec_mode
                await wurb_core.rec_worker.stop_recording()

            if rec_mode in ["mode-off"]:
                is_rec_mode_on = False
                is_scheduler_used = False
            elif rec_mode in ["mode-on", "mode-auto", "mode-manual"]:
                is_rec_mode_on = True
                is_scheduler_used = False
            elif rec_mode in ["mode-scheduler-on", "mode-scheduler-auto"]:
                is_rec_mode_on = True
                is_scheduler_used = True

            # Perform action.
            if is_rec_mode_on:
                wurb_core.rec_devices.check_capture_devices()
                is_mic_available = wurb_core.rec_devices.is_mic_available()
                if not is_mic_available:
                    # Try to find connected microphone.
                    # PyAudio has to be terminated and reloaded.
                    # wurb_core.audio.terminate()
                    # wurb_core.audio = wurb_core.pyaudio.PyAudio()

                    # wurb_core.audio_capture = wurb_utils.AudioCapture(wurb_core.audio, logger_name=wurb_core.logger_name)
                    # wurb_core.audio_playback = wurb_utils.AudioPlayback(wurb_core.audio, logger_name=wurb_core.logger_name)

                    wurb_core.rec_devices.get_capture_device_info()
                    is_mic_available = wurb_core.rec_devices.is_mic_available()

                if is_mic_available:
                    if is_scheduler_used:
                        # Check scheduler...
                        scheduler_on = wurb_core.rec_scheduler.check_scheduler()
                        if scheduler_on:
                            is_rec_to_be_activated = True
                            self.status_info_text = "Recording ON by scheduler"
                        else:
                            is_rec_to_be_activated = False
                            self.status_info_text = "Recording OFF by scheduler"
                    else:
                        is_rec_to_be_activated = True
                        self.status_info_text = "Recording ON"
                else:
                    is_rec_to_be_activated = False
                    self.status_info_text = "No microphone available"
            else:
                is_rec_to_be_activated = False
                self.status_info_text = "Recording OFF"

            # print("REC MANAGER: ", self.status_info_text)
            if self.status_info_text != self.status_info_text_old:
                self.status_info_text_old = self.status_info_text
                self.logger.info("Recording status: " + self.status_info_text)

            if is_rec_to_be_activated:
                wurb_core.rec_worker.start_recording()
            else:
                await wurb_core.rec_worker.stop_recording()

            self.trigger_rec_event()

        except Exception as e:
            message = "RecManager - check_status. Exception: " + str(e)
            self.logger.debug(message)

    def get_rec_event(self):
        """Used for synchronization."""
        if self.rec_event == None:
            self.rec_event = asyncio.Event()
        return self.rec_event

    def trigger_rec_event(self):
        """Used for synchronization."""
        # Create a new event and release the old.
        old_rec_event = self.get_rec_event()
        self.rec_event = asyncio.Event()
        old_rec_event.set()

    async def restart_rec(self):
        """ """
        try:
            await wurb_core.rec_worker.stop_recording()
            await asyncio.sleep(1.0)
            # await asyncio.sleep(3.0)
            await self.check_status()
        except Exception as e:
            message = "RecManager - restart_rec. Exception: " + str(e)
            self.logger.debug(message)

    async def get_status_dict(self):
        """ """
        try:
            # Avoid too long device names in the user interface.
            device_info = wurb_core.rec_devices.get_capture_device_info()
            device_name = device_info.get("device_name", "")
            device_freq_hz = device_info.get("sampling_freq_hz", "")
            device_name = device_name.replace("USB Ultrasound Microphone", "")
            if len(device_name) > 25:
                device_name = device_name[:24] + "..."
            status_dict = {
                "rec_status": self.status_info_text,
                "device_name": device_name,
                "sample_rate": str(device_freq_hz),
            }
            return status_dict
        except Exception as e:
            message = "RecManager - get_status_dict. Exception: " + str(e)
            self.logger.debug(message)

    async def manual_trigger(self):
        """ """
        try:
            # Will be checked and reset in wurb_sound_detection.py.
            self.manual_trigger_activated = True
            # Logging.
            message = "Manually triggered."
            self.logger.info(message)
        except Exception as e:
            message = "RecManager - manual_trigger. Exception: " + str(e)
            self.logger.debug(message)
