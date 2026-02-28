#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib

import wurb_core
from wurb_utils import SqliteDb


class WurbSettings(object):
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
        self.settings_event = None
        self.location_event = None
        self.latlong_event = None
        self.audiofeedback_event = None

    def configure(self):
        """ """

    async def startup(self, settings_dir):
        """ """
        try:
            # Connect to database.
            settings_db_path = pathlib.Path(settings_dir, "wurb_settings.db")
            self.settings_db = SqliteDb(
                db_file_path=settings_db_path, logger_name=self.logger_name
            )
            # Settings defaults.
            self.define_default_settings()
            self.define_default_location()
            # Load or populate database.
            globals = self.settings_db.get_values(identity="globals")
            if not globals:
                self.settings_db.set_values(
                    identity="globals", data_dict=self.default_globals
                )
            settings = self.settings_db.get_values(identity="settings")
            if not settings:
                self.settings_db.set_values(
                    identity="settings", data_dict=self.default_settings
                )
            location = self.settings_db.get_values(identity="location")
            if not location:
                self.settings_db.set_values(
                    identity="location", data_dict=self.default_location
                )
            startup_settings = self.settings_db.get_values(identity="startupSettings")
            if not startup_settings:
                self.settings_db.set_values(
                    identity="startupSettings", data_dict=self.default_settings
                )
            startup_location = self.settings_db.get_values(identity="startupLocation")
            if not startup_location:
                self.settings_db.set_values(
                    identity="startupLocation", data_dict=self.default_location
                )
            user_settings = self.settings_db.get_values(identity="userSettings")
            if not user_settings:
                self.settings_db.set_values(
                    identity="userSettings", data_dict=self.default_settings
                )
            user_location = self.settings_db.get_values(identity="userLocation")
            if not user_location:
                self.settings_db.set_values(
                    identity="userLocation", data_dict=self.default_location
                )
            # Select settings for startup.
            startup_option = self.settings_db.get_value(
                identity="globals", key="startupOption"
            )
            if startup_option == "startup-settings":
                settings = self.settings_db.get_values(identity="startupSettings")
                self.settings_db.set_values(identity="settings", data_dict=settings)
                location = self.settings_db.get_values(identity="startupLocation")
                self.settings_db.set_values(identity="location", data_dict=location)

            # GPS, action for last found GPS at startup.
            last_gps_at_startup = self.get_setting(key="lastGpsAtStartup")
            if last_gps_at_startup == "clear":
                location_db_dict = self.get_location_dict()
                location_db_dict["lastGpsLatitudeDd"] = 0.0
                location_db_dict["lastGpsLongitudeDd"] = 0.0
                self.settings_db.set_values(
                    identity="location", data_dict=location_db_dict
                )
            # Clear GPS.
            await self.save_latlong(0.0, 0.0)
        except Exception as e:
            message = "WurbSettings - startup. Exception: " + str(e)
            self.logger.debug(message)

    async def shutdown(self):
        """ """
        try:
            # Release events.
            if self.settings_event:
                self.settings_event.set()
            if self.location_event:
                self.location_event.set()
            if self.latlong_event:
                self.latlong_event.set()
            if self.audiofeedback_event:
                self.audiofeedback_event.set()
        except Exception as e:
            message = "WurbSettings - shutdown. Exception: " + str(e)
            self.logger.debug(message)

    def define_default_settings(self):
        """ """
        self.default_globals = {
            "startupOption": "as-last-session",
        }
        self.default_settings = {
            "recMode": "mode-off",
            "fileDirectory": "Station-1",
            "fileDirectoryDateOption": "date-post-before",
            "filenamePrefix": "wurb",
            "detectionLimitKhz": 17.0,
            "detectionSensitivityDbfs": -50,
            "detectionAlgorithm": "detection-simple",
            "recLengthS": 5,
            "recType": "FS",
            "feedbackOnOff": "feedback-off",
            "feedbackVolume": 50,
            "feedbackPitch": 30,
            "feedbackFilterLowKhz": 15,
            "feedbackFilterHighKhz": 150,
            "schedulerStartEvent": "on-sunset",
            "schedulerStartAdjust": -15,
            "schedulerStopEvent": "off-sunrise",
            "schedulerStopAdjust": 15,
            "schedulerPostAction": "post-none",
            "schedulerPostActionDelay": 5,
            "useGpsTime": "use-gps-time",
            "lastGpsAtStartup": "clear",
        }

    def define_default_location(self):
        """ """
        self.default_location = {
            "geoSource": "geo-not-used",
            "latitudeDd": 0.0,
            "longitudeDd": 0.0,
            "manualLatitudeDd": 0.0,
            "manualLongitudeDd": 0.0,
            "lastGpsLatitudeDd": 0.0,
            "lastGpsLongitudeDd": 0.0,
        }

    async def save_settings(self, settings_dict={}, settings_type=None):
        """ """
        try:
            settings_db_dict = self.settings_db.get_values(identity="settings")
            location_db_dict = self.settings_db.get_values(identity="location")

            if settings_type == "user-default":
                self.settings_db.set_values(
                    identity="userSettings", data_dict=settings_dict
                )
                self.settings_db.set_values(
                    identity="userLocation", data_dict=location_db_dict
                )
            if settings_type == "startup":
                self.settings_db.set_values(
                    identity="startupSettings", data_dict=settings_dict
                )
                self.settings_db.set_values(
                    identity="startupLocation", data_dict=location_db_dict
                )
            else:
                is_changed = False
                for key, value in settings_dict.items():
                    if value is not None:
                        # Clean up filename_prefix.
                        if key == "filenamePrefix":
                            value = value.replace(" ", "-")
                            value = value.replace("_", "-")
                        #
                        old_value = settings_db_dict.get(key, "")
                        settings_db_dict[key] = value
                        #
                        try:
                            if str(old_value) != str(value):
                                is_changed = True
                                # Logging.
                                message = (
                                    "Settings changed: "
                                    + str(key)
                                    + " from: "
                                    + str(old_value)
                                    + " to: "
                                    + str(value)
                                )
                                self.logger.debug(message)
                        except Exception as e:
                            # Logging.
                            message = "Error when comparing saved settings. " + str(e)
                            self.logger.debug(message)

                # Copy startupOption to global level.
                old_option = self.settings_db.get_value(
                    identity="globals", key="startupOption"
                )
                startup_option = settings_dict.get("startupOption", "")
                if startup_option != old_option:
                    is_changed = True
                    self.settings_db.set_value(
                        identity="globals", key="startupOption", value=startup_option
                    )
                # Save if changed and trigger events.
                if is_changed:
                    self.settings_db.set_values(
                        identity="settings", data_dict=settings_db_dict
                    )
                    # Trigger an event.
                    self.trigger_settings_event()
                    #
                    message = "Settings saved."
                    self.logger.info(message)

        except Exception as e:
            message = "WurbSettings - save_settings. Exception: " + str(e)
            self.logger.debug(message)

    def get_setting(self, key=None):
        """ """
        if key:
            return self.settings_db.get_value(identity="settings", key=key)
        return ""

    async def get_settings(self):
        """ """
        try:
            settings = self.settings_db.get_values(identity="settings")
            globals = self.settings_db.get_values(identity="globals")
            settings.update(globals)
            return settings
        except Exception as e:
            message = "WurbSettings - get_settings. Exception: " + str(e)
            self.logger.debug(message)

    async def load_settings(self, settings_type):
        """ """
        try:
            if settings_type == "user-default":
                settings = self.settings_db.get_values(identity="userSettings")
                self.settings_db.set_values(identity="settings", data_dict=settings)
                location = self.settings_db.get_values(identity="userLocation")
                self.settings_db.set_values(identity="location", data_dict=location)
            elif settings_type == "start-up":
                settings = self.settings_db.get_values(identity="startupSettings")
                self.settings_db.set_values(identity="settings", data_dict=settings)
                location = self.settings_db.get_values(identity="startupLocation")
                self.settings_db.set_values(identity="location", data_dict=location)
            elif settings_type == "factory-default":
                self.settings_db.set_values(
                    identity="globals", data_dict=self.default_globals
                )
                self.settings_db.set_values(
                    identity="settings", data_dict=self.default_settings
                )
                self.settings_db.set_values(
                    identity="location", data_dict=self.default_location
                )

            # Trigger events.
            self.trigger_settings_event()
            self.trigger_location_event()
        except Exception as e:
            message = "WurbSettings - load_settings. Exception: " + str(e)
            self.logger.debug(message)

    async def save_location(self, location_dict={}):
        """ """
        try:
            location_db_dict = self.get_location_dict()
            for key, value in location_dict.items():
                if value is not None:
                    location_db_dict[key] = value

            geo_source = location_db_dict["geoSource"]
            # Manual.
            if geo_source == "geo-manual":
                location_db_dict["latitudeDd"] = location_db_dict["manualLatitudeDd"]
                location_db_dict["longitudeDd"] = location_db_dict["manualLongitudeDd"]
            # GPS.
            if geo_source in ["geo-gps", "geo-gps-or-manual", "geo-last-gps-or-manual"]:
                location_db_dict["latitudeDd"] = 0.0
                location_db_dict["longitudeDd"] = 0.0
            # Save.
            self.settings_db.set_values(identity="location", data_dict=location_db_dict)
            # Trigger an event.
            self.trigger_location_event()
        except Exception as e:
            message = "WurbSettings - save_location. Exception: " + str(e)
            self.logger.debug(message)

    async def save_latlong(self, latitude_dd, longitude_dd):
        """ """
        try:
            location_db_dict = self.get_location_dict()
            geo_source = location_db_dict.get("geoSource", "")
            # If GPS.
            if geo_source in ["geo-gps", "geo-gps-or-manual", "geo-last-gps-or-manual"]:
                location_db_dict["latitudeDd"] = latitude_dd
                location_db_dict["longitudeDd"] = longitude_dd
                if (latitude_dd != 0.0) and (longitude_dd != 0.0):
                    location_db_dict["lastGpsLatitudeDd"] = latitude_dd
                    location_db_dict["lastGpsLongitudeDd"] = longitude_dd
            # Save.
            self.settings_db.set_values(identity="location", data_dict=location_db_dict)
            # Trigger an event.
            self.trigger_latlong_event()
        except Exception as e:
            message = "WurbSettings - save_latlong. Exception: " + str(e)
            self.logger.debug(message)

    def get_valid_location(self):
        """ """
        latitude = 0.0
        longitude = 0.0
        location_dict = self.get_location_dict()
        latitude = float(location_dict.get("latitudeDd", "0.0"))
        longitude = float(location_dict.get("longitudeDd", "0.0"))
        manual_latitude = float(location_dict.get("manualLatitudeDd", "0.0"))
        manual_longitude = float(location_dict.get("manualLongitudeDd", "0.0"))
        last_gps_latitude = float(location_dict.get("lastGpsLatitudeDd", "0.0"))
        last_gps_longitude = float(location_dict.get("lastGpsLongitudeDd", "0.0"))
        geo_source = location_dict.get("geoSource", "")
        if (latitude == 0.0) or (longitude == 0.0):
            if geo_source in ["geo-gps-or-manual"]:
                latitude = manual_latitude
                longitude = manual_longitude
        if (latitude == 0.0) or (longitude == 0.0):
            if geo_source in ["geo-last-gps-or-manual"]:
                latitude = last_gps_latitude
                longitude = last_gps_longitude
                if (latitude == 0.0) or (longitude == 0.0):
                    latitude = manual_latitude
                    longitude = manual_longitude
        # Result.
        return latitude, longitude

    def get_location_status(self):
        """ """
        lat, long = self.get_valid_location()
        if (lat == 0.0) and (long == 0.0):
            return "Not valid. Scheduler not started."
        else:
            geo_source = self.get_location_dict().get("geoSource", "")
            if geo_source == "geo-gps":
                if wurb_core.gps_reader:
                    no_of_satellites = wurb_core.gps_reader.get_number_of_satellites()
                    return "Number of satellites: " + str(no_of_satellites)
            else:
                return "Lat: " + str(lat) + " Long: " + str(long)

    def get_location_dict(self):
        """ """
        try:
            return self.settings_db.get_values(identity="location")
        except Exception as e:
            message = "WurbSettings - get_location_dict. Exception: " + str(e)
            self.logger.debug(message)

    async def get_location(self):
        """ """
        try:
            return self.settings_db.get_values(identity="location")
        except Exception as e:
            message = "WurbSettings - get_location. Exception: " + str(e)
            self.logger.debug(message)

    async def set_audio_feedback(self, volume, pitch):
        """ """
        try:
            self.settings_db.set_value(
                identity="settings", key="feedbackVolume", value=volume
            )
            self.settings_db.set_value(
                identity="settings", key="feedbackPitch", value=pitch
            )
            # audiofeedback = wurb_core.wurb_audiofeedback
            # if audiofeedback:
            #     await audiofeedback.set_volume(volume)
            #     await audiofeedback.set_pitch(pitch)
            # Trigger an event.
            self.trigger_audiofeedback_event()
        except Exception as e:
            message = "WurbSettings - set_audio_feedback. Exception: " + str(e)
            self.logger.debug(message)

    def trigger_settings_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_settings_event()
        self.settings_event = asyncio.Event()
        old_event.set()

    def get_settings_event(self):
        """ """
        if self.settings_event == None:
            self.settings_event = asyncio.Event()
        return self.settings_event

    def trigger_location_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_location_event()
        self.location_event = asyncio.Event()
        old_event.set()

    def get_location_event(self):
        """ """
        if self.location_event == None:
            self.location_event = asyncio.Event()
        return self.location_event

    def trigger_latlong_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_latlong_event()
        self.latlong_event = asyncio.Event()
        old_event.set()

    def get_latlong_event(self):
        """ """
        if self.latlong_event == None:
            self.latlong_event = asyncio.Event()
        return self.latlong_event

    def trigger_audiofeedback_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_audiofeedback_event()
        self.audiofeedback_event = asyncio.Event()
        old_event.set()

    def get_audiofeedback_event(self):
        """ """
        if self.audiofeedback_event == None:
            self.audiofeedback_event = asyncio.Event()
        return self.audiofeedback_event
