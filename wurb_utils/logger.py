#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import pathlib
import sys
import logging
from logging import handlers


class Logger(object):
    """ """

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)

    def get_logger_name(self):
        """ """
        return self.logger_name

    def setup_rotating_log(
        self,
        logging_dir="",
        log_name="info_log.txt",
        debug_log_name="debug_log.txt",
    ):
        """ """
        try:
            # Create directory for log files.
            logging_dir_path = pathlib.Path(logging_dir)
            if not logging_dir_path.exists():
                logging_dir_path.mkdir(parents=True)
            # Info and debug logging.
            logger_info = logging.getLogger(self.logger_name)
            logger_info.setLevel(logging.INFO)
            logger_debug = logging.getLogger(self.logger_name)
            logger_debug.setLevel(logging.DEBUG)
            logger_stdio = logging.getLogger(self.logger_name)
            logger_stdio.setLevel(logging.DEBUG)

            # Define rotation log files for info logger.
            log_info_name_path = pathlib.Path(logging_dir, log_name)
            log_handler = handlers.RotatingFileHandler(
                str(log_info_name_path), maxBytes=512 * 1024, backupCount=10
            )
            log_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)-8s : %(message)s ")
            )
            log_handler.setLevel(logging.INFO)
            logger_info.addHandler(log_handler)

            # Define rotation log files for debug logger.
            log_info_name_path = pathlib.Path(logging_dir, debug_log_name)
            log_handler = handlers.RotatingFileHandler(
                str(log_info_name_path), maxBytes=512 * 1024, backupCount=10
            )
            log_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)-8s : %(message)s ")
            )
            log_handler.setLevel(logging.DEBUG)
            logger_debug.addHandler(log_handler)

            # Define stdout logging.
            log_handler = logging.StreamHandler(sys.stdout)
            log_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(levelname)s : %(message)s")
            log_handler.setFormatter(formatter)
            logger_stdio.addHandler(log_handler)

        except Exception as e:
            print("Logger - Failed to setup logging: " + str(e))
