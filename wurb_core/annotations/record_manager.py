#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

# import asyncio
import logging
import pathlib
import platform

# import datetime
# import dateutil.parser
# import yaml

import wurb_core


class RecordManager(object):
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
        self.rec_sources = []
        self.rec_sources_by_id = {}

    def configure(self):
        """ """
        platform_os = platform.system()  # Linux, Windows or Darwin (for macOS).
        sources = wurb_core.config.get("annotations.sources")
        for source in sources:
            id = source.get("id", "")
            os = source.get("os", "")
            if id:
                if os in [platform_os, ""]:
                    # For rec_sources.
                    source_dict = {}
                    source_dict["id"] = source.get("id", "")
                    source_dict["name"] = source.get("name", "")
                    self.rec_sources.append(source_dict)
                    # For rec_sources_by_id.
                    self.rec_sources_by_id[id] = source

    def get_rec_sources(self):
        """ """
        return self.rec_sources

    def get_source_dir(self, source_id):
        """ """
        result = ""
        source = self.rec_sources_by_id.get(source_id, "")
        if source:
            executable_path_as_base = source.get("executable_path_as_base", False)
            media_path = source.get("media_path", "")
            rec_dir = source.get("rec_dir", "")
            if executable_path_as_base:
                result = pathlib.Path(wurb_core.executable_path, rec_dir).resolve()
            elif len(media_path) > 0:
                result = pathlib.Path(media_path, rec_dir).resolve()
            else:
                result = pathlib.Path(rec_dir).resolve()
        return result

    def get_rec_nights(self, source_id):
        """ """
        result = []
        source_dir_path = self.get_source_dir(source_id)
        if source_dir_path:
            if source_dir_path.exists():
                for dir2 in sorted(source_dir_path.iterdir()):
                    if dir2.is_dir():
                        if str(dir2.name) != "data":
                            night = {}
                            night["id"] = dir2.name
                            result.append(night)
        #
        return result

    def get_recordings(self, source_id, night_id):
        """ """
        result = []
        rec_files = self.get_rec_files(source_id, night_id)
        for rec_file in sorted(rec_files):
            rec_id = wurb_core.metadata.get_rec_id(rec_file)
            _prefix, _utc, local_date, local_time = wurb_core.metadata.get_rec_keys(
                rec_file
            )
            metadata = wurb_core.metadata.get_metadata(rec_file)
            result_dict = {}
            result_dict["recId"] = rec_id
            result_dict["localDate"] = str(local_date)
            result_dict["localTime"] = str(local_time)
            result_dict["peakKhz"] = metadata.get("peakKhz", "")
            result_dict["peakDbfs"] = metadata.get("peakDbfs", "")
            result_dict["latitude"] = metadata.get("latitude", "")
            result_dict["longitude"] = metadata.get("longitude", "")
            result.append(result_dict)
        #
        return result

    def get_rec_files(self, source_id, night_id):
        """ """
        result = []
        if (source_id) and (night_id):
            source_dir = pathlib.Path(self.get_source_dir(source_id)).resolve()
            night_dir = pathlib.Path(source_dir, night_id).resolve()
            if night_dir.exists():
                for record_file in sorted(night_dir.glob("*.wav")):
                    result.append(record_file)
        #
        return sorted(result)

    def get_rec_file(self, source_id, night_id, record_id):
        """ """
        result = ""
        if (source_id) and (night_id):  # and (record_id):
            source_dir = pathlib.Path(self.get_source_dir(source_id)).resolve()
            night_dir = pathlib.Path(source_dir, night_id).resolve()
            if night_dir.exists():
                recorded_files = sorted(night_dir.glob(record_id + "*.wav"))
                # if len(recorded_files) == 1:
                if len(recorded_files) > 0:
                    result = recorded_files[0]
                else:
                    print("ERROR...")
        #
        return result

    async def get_rec_info(self, source_id, night_id, record_id):
        """ """
        record_data = {
            "sourceId": source_id,
            "nightId": night_id,
            "recordId": record_id,
            "firstRecordId": "",
            "previousRecordId": "",
            "nextRecordId": "",
            "lastRecordId": "",
            "index": 0,
            "maxIndex": 0,
            "recordFile": "",
            "prefix": "",
            "localDate": "",
            "localTime": "",
            "dateTimeUtc": "",
            "latitude": "",
            "longitude": "",
            "quality": "",
            "tags": "",
            "comments": "",
            "peakKhz": "",
            "peakDbfs": "",
        }

        rec_file = self.get_rec_file(source_id, night_id, record_id)
        rec_files = self.get_rec_files(source_id, night_id)
        if (rec_file == "") and len(rec_files) > 0:
            if len(rec_files) > 0:
                rec_file = rec_files[0]
        if rec_file != "":
            (
                prefix,
                utc_datetime,
                local_date,
                local_time,
            ) = wurb_core.metadata.get_rec_keys(rec_file)
            metadata = wurb_core.metadata.get_metadata(rec_file)
            rec_ids = []
            for rec in sorted(rec_files):
                rec_ids.append(wurb_core.metadata.get_rec_id(rec))

            if not record_id in ["", None]:
                if not record_id in rec_ids:
                    print("ERROR: record_id is missing in the nights list.")

            first_record_id = ""
            previous_record_id = ""
            next_record_id = ""
            last_record_id = ""
            last_record_id = ""
            record_index = 0

            if len(rec_files) > 0:
                for index, rec_id in enumerate(rec_ids):
                    # Use first record if not specified.
                    if record_id in ["", None]:
                        record_id = rec_id
                    # Always add last record during iteration.
                    last_record_id = rec_id
                    # Add firsts record during first iteration.
                    if first_record_id == "":
                        first_record_id = rec_id
                    # Save index for current record.
                    if record_id == rec_id:
                        record_index = index + 1
                    # Save next record.
                    if next_record_id == "":
                        if rec_id > record_id:
                            next_record_id = rec_id
                    # Save previous record.
                    if rec_id < record_id:
                        previous_record_id = rec_id
                # If current record is the last one.
                if record_id == last_record_id:
                    next_record_id = last_record_id

            record_data = {
                "sourceId": source_id,
                "nightId": night_id,
                "recordId": record_id,
                "firstRecordId": first_record_id,
                "previousRecordId": previous_record_id,
                "nextRecordId": next_record_id,
                "lastRecordId": last_record_id,
                "index": str(record_index),
                "maxIndex": str(len(rec_files)),
                "recordFile": rec_file.name,
                "prefix": prefix,
                "localDate": str(local_date),
                "localTime": str(local_time),
                "dateTimeUtc": str(utc_datetime),
                "latitude": metadata.get("latitude", ""),
                "longitude": metadata.get("longitude", ""),
                "quality": metadata.get("annotationQuality", ""),
                "tags": metadata.get("annotationTags", ""),
                "comments": metadata.get("annotationComments", ""),
                "peakKhz": metadata.get("peakKhz", ""),
                "peakDbfs": metadata.get("peakDbfs", ""),
            }
        return record_data

    def set_rec_info(self, source_id, night_id, record_id, quality, tags, comments):
        """ """
        if (source_id) and (night_id) and (record_id):
            rec_file = self.get_rec_file(source_id, night_id, record_id)
            metadata = wurb_core.metadata.get_metadata(rec_file)
            metadata["annotationQuality"] = quality
            metadata["annotationTags"] = tags
            metadata["annotationComments"] = comments

            wurb_core.metadata.write_metadata(rec_file, metadata)

        record_data = {
            "sourceId": source_id,
            "nightId": night_id,
            "recordId": record_id,
            "quality": quality,
            "tags": tags,
            "comments": comments,
        }
        return record_data

    def get_rec_file_path(self, source_id, night_id, record_id):
        """ """
        file_path = ""
        if (source_id) and (night_id) and (record_id):
            file_path = str(self.get_rec_file(source_id, night_id, record_id))
        return str(file_path)
