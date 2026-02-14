#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import shutil

import wurb_core


class AdminCleanup(object):
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

    async def remove_q0(self, source_id, night_id):
        """ """
        wurb_core.admin_manager.update_db(source_id, night_id)
        if (source_id) and (night_id):
            quality_by_file = self.extract_quality(source_id, night_id)
            for file, quality in quality_by_file.items():
                if quality == "Q0":
                    rec_file_path = pathlib.Path(file)
                    if rec_file_path.exists():
                        rec_file_path.unlink()
                        print("WAV-FILE DELETED (Q0): ", str(rec_file_path))

            # Check if there are files left. If not, remove directory.
            rec_files = wurb_core.record_manager.get_rec_files(source_id, night_id)
            if len(rec_files) == 0:
                self.delete_monitoring_night(source_id, night_id)
            else:
                wurb_core.admin_manager.update_db(source_id, night_id)

            # TODO: Event trigger here...
        return {}

    async def remove_not_assigned(self, source_id, night_id):
        """ """
        wurb_core.admin_manager.update_db(source_id, night_id)
        if (source_id) and (night_id):
            quality_by_file = self.extract_quality(source_id, night_id)
            for file, quality in quality_by_file.items():
                if quality == "Not assigned":
                    rec_file_path = pathlib.Path(file)
                    if rec_file_path.exists():
                        rec_file_path.unlink()
                        print("WAV-FILE DELETED (NA): ", str(rec_file_path))

            wurb_core.admin_manager.update_db(source_id, night_id)
            # TODO: Event trigger here...

            # Check if there are files left. If not, remove directory.
            rec_files = wurb_core.record_manager.get_rec_files(source_id, night_id)
            if len(rec_files) == 0:
                await self.delete_monitoring_night(source_id, night_id)
            else:
                wurb_core.admin_manager.update_db(source_id, night_id)

            # TODO: Event trigger here...
        return {}

    async def delete_monitoring_night(self, source_id, night_id):
        """ """
        if (source_id) and (night_id):
            source_dir = pathlib.Path(
                wurb_core.record_manager.get_source_dir(source_id)
            ).resolve()
            night_dir = pathlib.Path(source_dir, night_id).resolve()
            if night_dir.exists():
                shutil.rmtree(night_dir)
                self.logger.info("Monitoring night deleted: " + night_id)

            # TODO: Event trigger here...

        return {}

    def extract_quality(self, source_id, night_id):
        """ """
        quality_by_file = {}
        if (source_id) and (night_id):
            # Get files for night.
            for rec_file in wurb_core.record_manager.get_rec_files(source_id, night_id):
                print("FILE: ", str(rec_file))
                # Get metadata for recording.
                metadata = wurb_core.metadata.get_metadata(rec_file)
                quality = metadata.get("annotationQuality", "")
                quality_by_file[str(rec_file)] = quality
        return quality_by_file
