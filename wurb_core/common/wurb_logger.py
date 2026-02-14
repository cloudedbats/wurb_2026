#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import datetime
import logging
from logging import handlers


class WurbLogger(object):
    """ """

    def __init__(self, config=None, logger_name="DefaultLogger"):
        """ """
        self.config = config
        if self.config == None:
            self.config = {}
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """
        self.logging_event = None
        self.client_messages = []

    def configure(self):
        """ """
        self.max_client_messages = self.config.get(
            "wurb_logger.max_client_messages", 10
        )

    def startup(self):
        """ """

    def shutdown(self):
        """ """
        if self.logging_event:
            self.logging_event.set()

    def info(self, message):
        """ """
        self.logger.info(message)
        self.write_log("info", message)

    def warning(self, message):
        """ """
        self.logger.warning(message)
        self.write_log("warning", message)

    def error(self, message):
        """ """
        self.logger.error(message)
        self.write_log("error", message)

    def debug(self, message):
        """ """
        self.logger.debug(message)
        # self.write_log("debug", message)

    def write_log(self, msg_type, message):
        """ """
        try:
            # Run the rest in the main asyncio event loop.
            datetime_local = datetime.datetime.now()
            asyncio.run_coroutine_threadsafe(
                self.write_log_async(msg_type, datetime_local, message),
                asyncio.get_event_loop(),
            )
        except Exception as e:
            # Can't log this, must use print.
            print("WurbLogger - write_log. Exception: ", e)

    async def write_log_async(self, msg_type, datetime_local, message):
        """ """
        try:
            time_str = datetime_local.strftime("%H:%M:%S")
            # datetime_str = datetime_local.strftime("%Y-%m-%d %H:%M:%S%z")
            if message:
                if msg_type in ["info", "warning", "error"]:
                    if msg_type in ["warning", "error"]:
                        self.client_messages.append(
                            time_str + " - " + msg_type.capitalize() + ": " + message
                        )
                    else:
                        self.client_messages.append(time_str + " - " + message)
                    # Log list too large. Remove oldest item.
                    if len(self.client_messages) > self.max_client_messages:
                        del self.client_messages[0]
                    # Trigger an event.
                    self.trigger_logging_event()
        except Exception as e:
            # Can't log this, must use print.
            print("WurbLogger - write_log_async. Exception: ", e)

    def trigger_logging_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_logging_event()
        self.logging_event = asyncio.Event()
        old_event.set()

    def get_logging_event(self):
        """ """
        if self.logging_event == None:
            self.logging_event = asyncio.Event()
        return self.logging_event

    def get_client_messages(self):
        """ """
        return self.client_messages[::-1]
