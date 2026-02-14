#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import os
import datetime
import pathlib
import psutil

import wurb_core


class RecStatus(object):
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
        # self.clear()
        # self.configure()

    async def rec_status(self):
        """ """
        try:
            # Available microphone.
            device_info = wurb_core.rec_devices.get_capture_device_info()
            device_name = device_info.get("device_name", "")
            sampling_freq_hz = device_info.get("sampling_freq_hz", "")
            if device_name:
                # Logging.
                message = "Connected microphone: "
                message += device_name
                message += ". Frequency: "
                message += str(sampling_freq_hz)
                message += " Hz."
                self.logger.info(message)
            else:
                # Logging.
                message = "No microphone is found. "
                self.logger.info(message)

            # Available speakers.
            device_info = wurb_core.rec_devices.get_playback_device_info()
            device_name = device_info.get("device_name", "")
            sampling_freq_hz = device_info.get("sampling_freq_hz", "")
            if device_name:
                # Logging.
                message = "Connected speaker: "
                message += device_name
                message += ". Frequency: "
                message += str(sampling_freq_hz)
                message += " Hz."
                self.logger.info(message)
            else:
                # Logging.
                message = "No speaker is found. "
                self.logger.info(message)

            # Solartime.
            latitude, longitude = wurb_core.wurb_settings.get_valid_location()
            if (latitude == 0.0) or (longitude == 0.0):
                message = "Can't calculate solartime. Lat/long is missing."
                self.logger.info(message)
                return

            sun_moon_dict = wurb_core.sun_moon.get_sun_moon_info(latitude, longitude)

            if sun_moon_dict:
                sunset = sun_moon_dict.get("sunset_local", None)
                dusk = sun_moon_dict.get("dusk_local", None)
                dawn = sun_moon_dict.get("dawn_local", None)
                sunrise = sun_moon_dict.get("sunrise_local", None)
                # moon_phase = sun_moon_dict.get("moon_phase", None)
                moon_phase_detailed = sun_moon_dict.get("moon_phase_detailed", None)
                if not sunset:
                    sunset = sun_moon_dict.get("sunset_comment", "")
                if not dusk:
                    dusk = sun_moon_dict.get("dusk_comment", "")
                if not dawn:
                    dawn = sun_moon_dict.get("dawn_comment", "")
                if not sunrise:
                    sunrise = sun_moon_dict.get("sunrise_comment", "")
                if sunset and dusk and dawn and sunrise and moon_phase_detailed:
                    message = ""
                    message += " Sunset: " + str(sunset)
                    message += " Dusk: " + str(dusk)
                    message += " Dawn: " + str(dawn)
                    message += " Sunrise: " + str(sunrise)
                    message += " Moon: " + moon_phase_detailed + "."
                    self.logger.info(message)
            else:
                # Logging.
                message = "Can't calculate solartime."
                self.logger.info(message)
        except Exception as e:
            message = "RecStatus - rec_status. Exception: " + str(e)
            self.logger.debug(message)
