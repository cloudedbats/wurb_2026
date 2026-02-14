#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib

import wurb_core


class AdminManager(object):
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

    def configure(self):
        """ """

    async def get_admin_info(self, source_id, night_id):
        """ """
        monitoring_night = ""
        directory_path = ""
        number_of_sound_files = 0
        result_array = (0, 0, 0, 0, 0)
        try:
            if night_id not in ["", "select"]:
                # Sync files and db content.
                await self.update_db(source_id, night_id)
                # Collect info.
                monitoring_night = night_id
                if (source_id) and (night_id):
                    dir_path = pathlib.Path(
                        wurb_core.record_manager.get_source_dir(source_id)
                    ).resolve()
                    directory_path = str(dir_path)
                    rec_files = wurb_core.record_manager.get_rec_files(
                        source_id, night_id
                    )
                    number_of_sound_files = len(rec_files)
                    # Get info from db.
                    night_dir = pathlib.Path(dir_path, night_id).resolve()
                    result_array = wurb_core.metadata.get_annotation_counts(
                        night_dir=night_dir
                    )
        except Exception as e:
            message = "AdminManager - get_admin_info. Exception: " + str(e)
            self.logger.debug(message)

        # Result dictionary.
        admin_info = {
            "monitoringNight": monitoring_night,
            "dirPath": directory_path,
            "numberOfSoundFiles": number_of_sound_files,
            "numberOfQ0": result_array[0],
            "numberOfQ1": result_array[1],
            "numberOfQ2": result_array[2],
            "numberOfQ3": result_array[3],
            "numberOfNoAssigned": result_array[4],
        }
        return admin_info

    async def update_db(self, source_id, night_id):
        """ """
        if (source_id) and (night_id):
            rec_dir_path = pathlib.Path(
                wurb_core.record_manager.get_source_dir(source_id)
            ).resolve()
            night_dir = pathlib.Path(rec_dir_path, night_id).resolve()
            # Get id dictionary for recordings.
            rec_id_dict = {}
            rec_files = wurb_core.record_manager.get_rec_files(source_id, night_id)
            for rec_file in rec_files:
                rec_id = wurb_core.metadata.get_rec_id(rec_file)
                rec_id_dict[rec_id] = str(rec_file)
            # Get unique id list from database.
            unique_ids = wurb_core.metadata.get_unique_ids(night_dir)
            # Remove from db if file is not present.
            remove_id_list = []
            for unique_id in unique_ids:
                if unique_id not in rec_id_dict:
                    remove_id_list.append(unique_id)
            if len(remove_id_list) > 0:
                wurb_core.metadata.delete_metadata(night_dir, remove_id_list)
