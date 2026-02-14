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
import platform

import wurb_core


class WurbRaspberryPi(object):
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
        self.os_debian = None
        self.rec_targets = []

    def configure(self):
        """ """
        self.rec_targets = wurb_core.config.get("record.targets")

    async def rpi_control(self, command):
        """ """
        # First check: Debian. Only valid for Debian OS.
        if self.is_os_debian():
            # Select command.
            if command == "rpiShutdown":
                await self.rpi_shutdown()
            elif command == "rpiReboot":
                await self.rpi_reboot()
            elif command == "rpi_sd_to_usb":
                await self.rpi_sd_to_usb()
            # elif command == "rpi_clear_sd_ok":
            elif command == "rpi_clear_sd":
                await self.rpi_clear_sd()
            else:
                # Logging.
                message = "Raspberry Pi command failed. Not a valid command: " + command
                self.logger.error(message)
        else:
            # Logging.
            message = "Raspberry Pi command failed (" + command + "), not Debian OS."
            self.logger.warning(message)

    async def set_detector_time(self, posix_time_s, cmd_source=""):
        """Only valid for Debian and user wurb."""
        try:
            local_datetime = datetime.datetime.fromtimestamp(posix_time_s)
            # utc_datetime = datetime.datetime.utcfromtimestamp(posix_time_s)
            # local_datetime = utc_datetime.replace(
            #     tzinfo=datetime.timezone.utc
            # ).astimezone(tz=None)
            time_string = local_datetime.strftime("%Y-%m-%d %H:%M:%S")
            print(time_string)
            # Logging.
            message = "Detector time update: " + time_string
            if cmd_source:
                message += " (" + cmd_source + ")."
            self.logger.info(message)
            # First check: OS Raspbian.
            if self.is_os_debian():
                # Second check: User wurb exists. Perform: "date --set".
                os.system('cd /home/wurb && sudo date --set "' + time_string + '"')
            else:
                # Logging.
                message = "Detector time update failed, not Debian OS."
                self.logger.warning(message)
        except Exception as e:
            message = "WurbRaspberryPi - set_detector_time. Exception: " + str(e)
            self.logger.debug(message)

    # def get_settings_dir_path(self):
    #     """ """
    #     rpi_dir_path = "/home/wurb/"  # For RPi SD card with user 'wurb'.
    #     # Default for not Debian.
    #     dir_path = pathlib.Path("wurb_settings")
    #     if pathlib.Path(rpi_dir_path).exists():
    #         dir_path = pathlib.Path(rpi_dir_path, "wurb_settings")
    #     # Create directories.
    #     if not dir_path.exists():
    #         dir_path.mkdir(parents=True)
    #     return dir_path

    def get_wavefile_target_dir_path(self):
        """
        Example from wurb_config_default.txt:
            record:
              targets:
                - id: sda1
                  name: USB-1
                  os: Linux
                  media_path: /media/USB-sda1
                  rec_dir: wurb_recordings
                - id: sdb1
                  name: USB-2
                  os: Linux
                  media_path: /media/USB-sdb1
                  rec_dir: wurb_recordings
                - id: local
                  name: Local
                  executable_path_as_base: true
                  rec_dir: ../wurb_recordings
                  free_disk_limit: 500 # Unit MB.
        """
        try:
            platform_os = platform.system()  # Linux, Windows or Darwin (for macOS).
            used_dir_path = None
            # Check targets for recordings.
            for rec_target in self.rec_targets:
                if used_dir_path == None:
                    os = rec_target.get("os", "")
                    executable_path_as_base = rec_target.get(
                        "executable_path_as_base", False
                    )
                    media_path = rec_target.get("media_path", "")
                    rec_dir = rec_target.get("rec_dir", "")
                    free_disk_limit = rec_target.get("free_disk_limit", 100)  # Unit MB.
                    #
                    if executable_path_as_base:
                        base_path = pathlib.Path(wurb_core.executable_path)
                        used_dir_path = base_path
                    elif len(media_path) > 0:
                        if os in [platform_os, ""]:
                            # Directory may exist even when no USB attached.
                            # Use is_mount instead of exists on Linux.
                            media_path = pathlib.Path(media_path)
                            if platform_os == "Linux":
                                if media_path.is_mount():
                                    used_dir_path = media_path
                            else:
                                if media_path.exists():
                                    used_dir_path = media_path
                    else:
                        used_dir_path = pathlib.Path(".")

                    # Check if enough space is avaialble.
                    if used_dir_path != None:
                        hdd = psutil.disk_usage(str(used_dir_path))
                        free_disk = hdd.free / (2**20)  # To MB.
                        free_disk_limit = float(free_disk_limit)
                        if free_disk >= free_disk_limit:
                            # Return path.
                            return pathlib.Path(used_dir_path, rec_dir).resolve()

            message = "Not enough space left to store recordings."
            self.logger.error(message)
            return None
        except Exception as e:
            message = "Failed to find media for recordings. Exception: " + str(e)
            self.logger.debug(message)

        return None

        # Example code for psutil.disk_usage:
        # hdd = psutil.disk_usage(str(dir_path))
        # total_disk = hdd.total / (2**20)
        # used_disk = hdd.used / (2**20)
        # free_disk = hdd.free / (2**20)
        # percent_disk = hdd.percent
        # print("Total disk: ", total_disk, "MB")
        # print("Used disk: ", used_disk, "MB")
        # print("Free disk: ", free_disk, "MB")
        # print("Percent: ", percent_disk, "%")

    def is_os_debian(self):
        """Check OS version for Raspberry Pi."""
        if self.os_debian is not None:
            return self.os_debian
        else:
            try:
                os_version_path = pathlib.Path("/etc/os-release")
                if os_version_path.exists():
                    with os_version_path.open("r") as os_file:
                        os_file_content = os_file.read()
                        # print("Content of /etc/os-release: ", os_file_content)
                        if "DEBIAN" in os_file_content.upper():
                            self.os_debian = True
                        else:
                            self.os_debian = False
                else:
                    self.os_debian = False
            except Exception as e:
                message = "WurbRaspberryPi - is_os_debian. Exception: " + str(e)
                self.logger.debug(message)
        #
        return self.os_debian

    async def rpi_shutdown(self):
        """ """
        # Logging.
        message = "The Raspberry Pi command 'Shutdown' is activated."
        self.logger.info(message)
        await asyncio.sleep(1.0)
        #
        os.system("cd /home/wurb && sudo shutdown -h now")

    async def rpi_reboot(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Reboot' is activated."
            self.logger.info(message)
            await asyncio.sleep(1.0)
            #
            os.system("cd /home/wurb && sudo reboot")
        except Exception as e:
            message = "WurbRaspberryPi - rpi_reboot. Exception: " + str(e)
            self.logger.debug(message)

    async def rpi_sd_to_usb(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Copy SD to USB' is not implemented."
            self.logger.info(message)
        except Exception as e:
            message = "WurbRaspberryPi - rpi_sd_to_usb. Exception: " + str(e)
            self.logger.debug(message)

    async def rpi_clear_sd(self):
        """ """
        try:
            # Logging.
            message = "The Raspberry Pi command 'Clear SD card' is not implemented."
            self.logger.info(message)
        except Exception as e:
            message = "WurbRaspberryPi - rpi_clear_sd. Exception: " + str(e)
            self.logger.debug(message)
