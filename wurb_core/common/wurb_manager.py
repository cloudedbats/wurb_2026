#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import datetime
import time

import wurb_core


class WurbManager(object):
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
        # self.wurb_loop = None

    def configure(self):
        """ """
        # self.max_client_messages = self.config.get(
        #     "wurb_logger.max_client_messages", self.max_client_messages
        # )

    def startup(self):
        """ """
        wurb_core.wurb_logger.startup()
        wurb_core.rec_manager.startup()
        self.wurb_loop = asyncio.create_task(
            self.wurb_control_loop(), name="Wurb manager control loop"
        )

    async def shutdown(self):
        """ """
        try:
            # await wurb_core.wurb_logger.shutdown()
            await wurb_core.rec_manager.shutdown()
            if self.wurb_loop:
                self.wurb_loop.cancel()

            # Get a list of all running tasks.
            await asyncio.sleep(0)
            all_running_tasks = asyncio.all_tasks()
            # Remove current task from list.
            current_task = asyncio.current_task()
            all_running_tasks.remove(current_task)
            # Cancel all remaining tasks.
            self.logger.debug(
                "WurbManager shutdown. Number of remaining tasks: "
                + str(len(all_running_tasks))
            )
            for task in all_running_tasks:
                task_name = task.get_name()
                self.logger.debug("- Cancel task: " + task_name)
                task.cancel()
        except Exception as e:
            message = "WurbManager - shutdown. Exception: " + str(e)
            self.logger.debug(message)

    async def wurb_control_loop(self):
        """ """
        try:
            while True:
                # Create activity log.
                rec_file_writer = wurb_core.RecFileWriter()
                target_path = rec_file_writer.prepare_rec_target_dir()
                data_dir_path = pathlib.Path(target_path, "data")
                if not data_dir_path.exists():
                    data_dir_path.mkdir(parents=True)
                activity_log_path = pathlib.Path(data_dir_path, "wurb_activity.csv")
                if not activity_log_path.exists():
                    with activity_log_path.open("w") as log_file:
                        # Write header.
                        log_file.write(
                            "Datetime UTC,Local date,Local time,Latitude,Longitude,Recording status\n"
                        )
                # Add row.
                utc_datetime_str = time.strftime("%Y%m%dT%H%M%S%z", time.localtime())
                date_str = time.strftime("%Y-%m-%d")
                time_str = time.strftime("%H:%M:%S")
                status_dict = await wurb_core.rec_manager.get_status_dict()
                rec_status = status_dict.get("rec_status", "")
                if rec_status not in [
                    "",
                    "No microphone available",
                    "Recording OFF",
                    # "Recording OFF by scheduler",
                ]:
                    latitude, longitude = wurb_core.wurb_settings.get_valid_location()
                    with activity_log_path.open("a") as log_file:
                        # Write row.
                        log_file.write(
                            utc_datetime_str
                            + ","
                            + date_str
                            + ","
                            + time_str
                            + ","
                            + str(latitude)
                            + ","
                            + str(longitude)
                            + ","
                            + rec_status
                            + "\n"
                        )
                # Sleep until after next minute.
                sleep_time = 60.5 - (time.time() % 60)
                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            self.logger.debug("Wurb control loop was cancelled.")
        except Exception as e:
            message = "WurbManager - wurb_control_loop. Exception: " + str(e)
            self.logger.debug(message)
