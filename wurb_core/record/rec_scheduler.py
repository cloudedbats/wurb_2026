#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import datetime

import wurb_core


class WurbScheduler(object):
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
        self.solartime_last_used_key = ""

    def configure(self):
        """ """

    def check_scheduler(self):
        """ """
        is_rec_active = False
        # Start/stop time.
        start_event_local, stop_event_local = self.calculate_start_stop()

        if (start_event_local is None) or (stop_event_local is None):
            # Can't calculate start or stop.
            is_rec_active = False
            return is_rec_active

        # Evaluate action.
        now_local = datetime.datetime.now().astimezone()
        if start_event_local == stop_event_local:
            # Always off.
            is_rec_active = False
        elif start_event_local < stop_event_local:
            # Same day.
            if (start_event_local < now_local) and (now_local < stop_event_local):
                is_rec_active = True
            else:
                is_rec_active = False
        else:
            # Different days.
            start_local_new = start_event_local
            stop_local_new = stop_event_local
            # Prepare.
            if now_local < stop_event_local:
                start_local_new = start_event_local - datetime.timedelta(days=1)
            if now_local > stop_event_local:
                stop_local_new = stop_event_local + datetime.timedelta(days=1)
            # Check.
            if (start_local_new < now_local) and (now_local < stop_local_new):
                is_rec_active = True
            else:
                is_rec_active = False

        return is_rec_active

    def calculate_start_stop(self):
        """ """
        # Get settings.
        start_event = wurb_core.wurb_settings.get_setting("schedulerStartEvent")
        start_event_adjust = wurb_core.wurb_settings.get_setting("schedulerStartAdjust")
        stop_event = wurb_core.wurb_settings.get_setting("schedulerStopEvent")
        stop_event_adjust = wurb_core.wurb_settings.get_setting("schedulerStopAdjust")
        # Get sunset, sunrise, etc.
        solartime_dict = self.get_solartime_data()
        # Start event.
        if start_event in ["on-sunset", "on-dusk", "on-dawn", "on-sunrise"]:
            if not solartime_dict:
                # Lat/long needed to calculate start.
                return (None, None)
            start_event = start_event.replace("on-", "") + "_local"
            start_local = solartime_dict.get(start_event, None)
            start_event_local = datetime.datetime.now().astimezone()
            start_event_local = start_event_local.replace(
                hour=start_local.hour,
                minute=start_local.minute,
                second=start_local.second,
                microsecond=0,
            )
        else:
            start_event = start_event.replace("on-", "")
            start_event_hour = int(float(start_event))
            start_event_local = datetime.datetime.now().astimezone()
            start_event_local = start_event_local.replace(
                hour=start_event_hour, minute=0, second=0, microsecond=0
            )
        # Stop event.
        if stop_event in ["off-sunset", "off-dusk", "off-dawn", "off-sunrise"]:
            if not solartime_dict:
                # Lat/long needed to calculate stop.
                return (None, None)
            stop_event = stop_event.replace("off-", "") + "_local"
            stop_local = solartime_dict.get(stop_event, None)
            stop_event_local = datetime.datetime.now().astimezone()
            stop_event_local = stop_event_local.replace(
                hour=stop_local.hour,
                minute=stop_local.minute,
                second=stop_local.second,
                microsecond=0,
            )
        else:
            stop_event = stop_event.replace("off-", "")
            stop_event_hour = int(float(stop_event))
            stop_event_local = datetime.datetime.now().astimezone()
            stop_event_local = stop_event_local.replace(
                hour=stop_event_hour, minute=0, second=0, microsecond=0
            )
        # Adjust time.
        start_event_local += datetime.timedelta(minutes=int(float(start_event_adjust)))
        stop_event_local += datetime.timedelta(minutes=int(float(stop_event_adjust)))

        return (start_event_local, stop_event_local)

    def get_solartime_data(self, print_new=True):
        """ """
        latitude, longitude = wurb_core.wurb_settings.get_valid_location()
        if (latitude == 0.0) or (longitude == 0.0):
            # No lat/long found.
            return None

        date_local = datetime.datetime.now().date()
        latitude_short = round(latitude, 2)
        longitude_short = round(longitude, 2)

        sun_moon_dict = wurb_core.sun_moon.get_sun_moon_info(
            latitude_short, longitude_short
        )

        used_key = (
            str(date_local) + "<->" + str(latitude_short) + "<->" + str(longitude_short)
        )
        if used_key != self.solartime_last_used_key:
            self.solartime_last_used_key = used_key
            # Logging.
            sunset_local = sun_moon_dict.get("sunset_local", None)
            dusk_local = sun_moon_dict.get("dusk_local", None)
            dawn_local = sun_moon_dict.get("dawn_local", None)
            sunrise_local = sun_moon_dict.get("sunrise_local", None)
            if sunset_local and dusk_local and dawn_local and sunrise_local:
                if print_new:
                    # sunset_local = self.utc_to_local(sunset_utc)
                    # dusk_local = self.utc_to_local(dusk_utc)
                    # dawn_local = self.utc_to_local(dawn_utc)
                    # sunrise_local = self.utc_to_local(sunrise_utc)
                    message = "Solartime recalculated: "
                    # message += " Date: " + str(date_local)
                    message += " Latitude: " + str(latitude_short)
                    message += " Longitude: " + str(longitude_short)
                    message += " Sunset: " + sunset_local.strftime("%H:%M:%S")
                    message += " Dusk: " + dusk_local.strftime("%H:%M:%S")
                    message += " Dawn: " + dawn_local.strftime("%H:%M:%S")
                    message += " Sunrise: " + sunrise_local.strftime("%H:%M:%S")
                    self.logger.info(message)
            else:
                return None

        return sun_moon_dict
