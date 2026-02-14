#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import sqlite3


class SqliteDb(object):
    """ """

    def __init__(self, db_file_path="./sqlite_db.db", logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.db_file_path = pathlib.Path(db_file_path)
        self.clear()

    def clear(self):
        """ """
        self.db_conn = None

    def create_db(self):
        """ """
        if not self.db_file_path.exists():
            self.db_conn = sqlite3.connect(self.db_file_path)
            c = self.db_conn.cursor()
            command = "CREATE TABLE key_value_data ("
            command += "identity VARCHAR NOT NULL, "
            command += "key VARCHAR NOT NULL, "
            command += "value VARCHAR, "
            command += "PRIMARY KEY (identity, key)"
            command += ")"
            c.execute(command)
            self.db_conn.commit()

    def connect(self):
        """ """
        self.create_db()
        if self.db_conn == None:
            self.db_conn = sqlite3.connect(self.db_file_path)

    def disconnect(self):
        """ """
        if self.db_conn != None:
            self.db_conn.close()
            self.db_conn = None

    def set_value(self, key, value, identity="NA"):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "INSERT OR IGNORE INTO key_value_data "
            command += "(identity, key, value) "
            command += "VALUES (?, ?, ?) "
            c.execute(
                command,
                (
                    identity,
                    key,
                    value,
                ),
            )
            command = "UPDATE key_value_data "
            command += "SET value = ? "
            command += "WHERE identity = ? "
            command += "AND key = ? "
            c.execute(
                command,
                (
                    value,
                    identity,
                    key,
                ),
            )
            self.db_conn.commit()
        finally:
            c.close()
            self.disconnect()

    def get_value(self, key, identity="NA"):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "SELECT value FROM key_value_data "
            command += "WHERE identity = ? "
            command += "AND key = ? "
            c.execute(
                command,
                (
                    identity,
                    key,
                ),
            )
            result_dict = c.fetchone()
            result = ""
            if result_dict and len(result_dict) >= 1:
                result = result_dict[0]
            return result
        finally:
            c.close()
            self.disconnect()

    def set_values(self, data_dict, identity="NA"):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command_i = "INSERT OR IGNORE INTO key_value_data "
            command_i += "(identity, key, value) "
            command_i += "VALUES (?, ?, ?) "

            command_u = "UPDATE key_value_data "
            command_u += "SET value = ? "
            command_u += "WHERE identity = ? "
            command_u += "AND key = ? "
            for key, value in data_dict.items():
                c.execute(
                    command_i,
                    (
                        identity,
                        key,
                        value,
                    ),
                )
                c.execute(
                    command_u,
                    (
                        value,
                        identity,
                        key,
                    ),
                )
            self.db_conn.commit()
        finally:
            c.close()
            self.disconnect()

    def get_values(self, identity="NA"):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "SELECT key, value FROM key_value_data "
            command += "WHERE identity = ? "
            c.execute(command, (identity,))
            result_dict = {}
            for row in c.fetchall():
                result_dict[row[0]] = row[1]
            return result_dict
        finally:
            c.close()
            self.disconnect()

    def delete_rows(self, identity_list):
        """ """
        self.connect()
        try:
            c = self.db_conn.cursor()
            command = "DELETE FROM key_value_data "
            command += "WHERE identity = ? "
            for identity in identity_list:
                c.execute(command, (identity,))
            self.db_conn.commit()
        finally:
            c.close()
            self.disconnect()
