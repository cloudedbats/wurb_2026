#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import pathlib
import yaml
import logging


class Configuration:
    """ """

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.clear()

    def clear(self):
        """ """
        self.config = {}
        self.config_default = {}

    def load_config(
        self,
        config_dir="",
        config_file="config.yaml",
        config_default_file="config_default.yaml",
    ):
        """ """
        self.clear()
        # Check if config file exists.
        config_default_path = pathlib.Path(config_default_file)
        config_path = pathlib.Path(config_dir, config_file)
        if not config_path.exists():
            if not config_path.parent.exists():
                config_path.parent.mkdir(parents=True)
            config_path.write_text(config_default_path.read_text())
            self.logger.debug(
                "Configuration - Config file missing. Copy of default config made: " + config_path.name
            )
        # Load config files.
        with open(config_default_path) as file:
            self.config_default = yaml.load(file, Loader=yaml.FullLoader)
        with open(config_path) as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

    def get(self, key_path, default=""):
        """ """
        result = default
        value = self.get_value(key_path)
        if value:
            result = value
        return result

    def get_value(self, key_path):
        """ """
        result = ""
        config_dict = self.config
        config_default_dict = self.config_default

        key_parts = key_path.split(".")
        for key_part in key_parts:
            if key_part in config_dict:
                config_dict = config_dict[key_part]
            else:
                config_dict = ""
                break
        result = config_dict

        if not result:
            for key_part in key_parts:
                if key_part in config_default_dict:
                    config_default_dict = config_default_dict[key_part]
                else:
                    config_default_dict = ""
                    break
            result = config_default_dict

        return result
