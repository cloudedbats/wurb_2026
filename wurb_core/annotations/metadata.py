#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import datetime
import dateutil.parser
import yaml

import wurb_core
from wurb_utils import SqliteDb


class Metadata(object):
    """ """

    def __init__(self, config=None, logger=None, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logger
        self.logger_name = logger_name
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
        # self.metadata_header_rows = [
        #     "# Metadata for CloudedBats WURB-2026.",
        #     "#" "---",
        # ]

    def get_data_dir(self, rec_file_path):
        """ """
        file_path = pathlib.Path(rec_file_path)
        parent_dir = file_path.parent
        data_dir_path = pathlib.Path(parent_dir, "data").resolve()
        if not data_dir_path.exists():
            data_dir_path.mkdir(parents=True)
        #
        return data_dir_path

    def get_metadata_file_path(self, rec_file_path):
        """ """
        data_dir = self.get_data_dir(rec_file_path)
        prefix, utc_datetime, local_date, local_time = self.get_rec_keys(rec_file_path)
        datetime_str = (
            str(local_date).replace("-", "") + "T" + str(local_time).replace(":", "")
        )
        metadata_file_path = pathlib.Path(
            data_dir, prefix + "_" + datetime_str + "_metadata.yaml"
        ).resolve()
        #
        return metadata_file_path

    def get_rec_id(self, rec_file_path):
        """ """
        data_dir = self.get_data_dir(rec_file_path)
        prefix, utc_datetime, local_date, local_time = self.get_rec_keys(rec_file_path)
        datetime_str = (
            str(local_date).replace("-", "") + "T" + str(local_time).replace(":", "")
        )
        rec_id = prefix + "_" + datetime_str
        #
        return rec_id

    def get_rec_keys(self, rec_file_path):
        """ """
        file_name = pathlib.Path(rec_file_path).name
        parts = file_name.split("_")
        prefix = parts[0]
        utc_datetime_str = parts[1]
        utc_datetime = dateutil.parser.isoparse(utc_datetime_str)
        local_date = utc_datetime.date()
        local_time = utc_datetime.time()
        #
        return prefix, utc_datetime, local_date, local_time

    def add_basic_metadata(self, rec_file_path):
        """ """
        rec_file_path = pathlib.Path(rec_file_path)
        prefix, utc_datetime, local_date, local_time = self.get_rec_keys(rec_file_path)
        metadata = {}
        metadata["recFileName"] = rec_file_path.name
        metadata["prefix"] = prefix
        metadata["dateTimeUtc"] = str(utc_datetime)
        metadata["dateLocal"] = str(local_date)
        metadata["timeLocal"] = str(local_time)
        metadata["annotationQuality"] = "Not assigned"
        metadata["annotationTags"] = ""
        metadata["annotationComments"] = ""
        #
        self.write_metadata(rec_file_path, metadata)

    def read_metadata(self, rec_file_path):
        """ """
        data_dir = self.get_data_dir(rec_file_path)
        rec_id = self.get_rec_id(rec_file_path)
        db_path = pathlib.Path(data_dir, "metadata.db")
        metadata_db = MetadataSqliteDb(
            db_file_path=db_path, logger_name=self.logger_name
        )
        metadata = metadata_db.get_values(identity=rec_id)
        if not metadata:
            self.add_basic_metadata(rec_file_path)
            metadata = metadata_db.get_values(identity=rec_id)
        #
        return metadata

    def write_metadata(self, rec_file_path, metadata):
        """ """
        data_dir = self.get_data_dir(rec_file_path)
        rec_id = self.get_rec_id(rec_file_path)
        db_path = pathlib.Path(data_dir, "metadata.db")
        metadata_db = MetadataSqliteDb(
            db_file_path=db_path, logger_name=self.logger_name
        )
        # flat_metadata = self.flatten_metadata(metadata)
        metadata_db.set_values(metadata, identity=rec_id)

    def get_metadata(self, rec_file_path):
        """ """
        metadata = {}
        rec_file_path = pathlib.Path(rec_file_path).resolve()
        # Read metadata from file.
        metadata = self.read_metadata(rec_file_path)
        #
        return metadata

    def get_annotation_counts(self, night_dir):
        """ """
        db_path = pathlib.Path(night_dir, "data", "metadata.db")
        metadata_db = MetadataSqliteDb(
            db_file_path=db_path, logger_name=self.logger_name
        )
        metadata = metadata_db.get_annotation_counts()
        #
        return metadata

    def get_unique_ids(self, night_dir):
        """ """
        db_path = pathlib.Path(night_dir, "data", "metadata.db")
        metadata_db = MetadataSqliteDb(
            db_file_path=db_path, logger_name=self.logger_name
        )
        unique_ids = metadata_db.get_unique_ids()
        #
        return unique_ids

    def delete_metadata(self, night_dir, remove_id_list):
        """ """
        db_path = pathlib.Path(night_dir, "data", "metadata.db")
        metadata_db = MetadataSqliteDb(
            db_file_path=db_path, logger_name=self.logger_name
        )
        metadata_db.delete_rows(identity_list=remove_id_list)


class MetadataSqliteDb(SqliteDb):
    """ """

    def __init__(self, db_file_path, logger_name="DefaultLogger"):
        """ """
        super().__init__(db_file_path, logger_name)

    def get_unique_ids(self):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "SELECT DISTINCT identity FROM key_value_data "
            command += "ORDER BY identity "
            c.execute(command)
            results = c.fetchall()
            result_list = []
            for result in results:
                result_list.append(result[0])
            return result_list
        finally:
            c.close()

    def get_annotation_counts(self):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "SELECT "
            command += "( "
            command += "SELECT COUNT(*) FROM key_value_data "
            command += "WHERE key = 'annotationQuality' AND value = 'Q0'"
            command += ") count_q0, "
            command += "( "
            command += "SELECT COUNT(*) FROM key_value_data "
            command += "WHERE key = 'annotationQuality' AND value = 'Q1'"
            command += ") count_q1, "
            command += "( "
            command += "SELECT COUNT(*) FROM key_value_data "
            command += "WHERE key = 'annotationQuality' AND value = 'Q2'"
            command += ") count_q2, "
            command += "( "
            command += "SELECT COUNT(*) FROM key_value_data "
            command += "WHERE key = 'annotationQuality' AND value = 'Q3'"
            command += ") count_q3, "
            command += "( "
            command += "SELECT COUNT(*) FROM key_value_data "
            command += "WHERE key = 'annotationQuality' AND value = 'Not assigned'"
            command += ") count_na "

            c.execute(command)
            result = c.fetchone()
            return result
        finally:
            c.close()
