#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import wurb_core


class RecDevices(object):
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
        self.config_capture_devices = []
        self.configure()

    def clear(self):
        """ """
        # Capture.
        self.capture_device = None

    def configure(self):
        """ """
        # Capture.
        self.config_capture_devices = wurb_core.config.get("audio_capture")

    def get_capture_device_info(self):
        """ """
        if self.capture_device == None:
            self.check_capture_devices()
        #
        return self.capture_device

    def is_mic_available(self):
        """ """
        if self.capture_device in [None, {}]:
            return False
        else:
            return True

    def check_capture_devices(self):
        capture_device = {}
        try:
            #
            available_devices = wurb_core.audio_capture.get_capture_devices()
            #
            for config_device_dict in self.config_capture_devices:
                try:
                    config_name_part = config_device_dict["device_name"]
                    for device_dict in available_devices:
                        device_full_name = device_dict["device_name"]
                        if config_name_part in device_full_name:
                            capture_device = device_dict
                            # Adjust to config.
                            if "sampling_freq_hz" in config_device_dict:
                                config_sampling_freq_hz = config_device_dict[
                                    "sampling_freq_hz"
                                ]
                                capture_device["sampling_freq_hz"] = (
                                    config_sampling_freq_hz
                                )
                            if "channels" in config_device_dict:
                                capture_device["config_channels"] = (
                                    config_device_dict.get("channels", "")
                                )
                            # Done.
                            self.capture_device = capture_device
                            return
                    # Also check if Pettersson M500.
                    if wurb_core.m500.is_m500_available():
                        device_name = wurb_core.m500.device_name
                        if config_name_part in device_name:
                            capture_device = {}
                            capture_device["device_index"] = 9999
                            capture_device["device_name"] = device_name
                            capture_device["input_channels"] = 1
                            capture_device["config_channels"] = "MONO"
                            capture_device["sampling_freq_hz"] = (
                                wurb_core.m500.sampling_freq_hz
                            )
                            # Done.
                            self.capture_device = capture_device
                            return
                except Exception as e:
                    message = "RecDevices - check_capture_devices-1. Exception: "
                    message += str(e)
                    self.logger.debug(message)
            # Not found.
            self.capture_device = {}
        except Exception as e:
            message = "RecDevices - check_capture_devices-2. Exception: " + str(e)
            self.logger.debug(message)
