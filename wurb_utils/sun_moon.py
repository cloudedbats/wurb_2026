#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import astral
import astral.sun
import astral.moon
import datetime
import dateutil.parser


class SunMoon:
    """ """

    def __init__(self):
        """ """
        self.clear()

    def clear(self):
        """ """
        self.memory_cache_dict = {}

    def get_sun_moon_info(
        self,
        latitude=60.0,
        longitude=15.0,
        date=str(datetime.date.today()),
    ):
        """ """
        # Date and position formats.
        date = dateutil.parser.parse(str(date))
        latitude = float(latitude)
        longitude = float(longitude)

        # Check if already calculated.
        latitude_short = round(latitude, 3)  # Accuracy 110 m.
        longitude_short = round(longitude, 3)  # Depends on latitude, <= 110 m.
        cache_key = (
            str(date) + "<->" + str(latitude_short) + "<->" + str(longitude_short)
        )
        if cache_key in self.memory_cache_dict:
            return self.memory_cache_dict[cache_key]

        # Results.
        result_dict = {
            "latitude_dd": latitude,
            "longitude_dd": longitude,
            "date": str(date.date()),
            "dawn_utc": None,
            "sunrise_utc": None,
            "sunset_utc": None,
            "dusk_utc": None,
            "moonrise_utc": None,
            "moonset_utc": None,
            "moon_phase_0to28": None,
            "moon_phase": None,
            "moon_phase_detailed": None,
            "dawn_comment": "",
            "sunrise_comment": "",
            "sunset_comment": "",
            "dusk_comment": "",
            "moonrise_comment": "",
            "moonset_comment": "",
        }
        # Calculate.
        observer = astral.Observer(latitude=latitude, longitude=longitude)
        try:
            dawn_utc = astral.sun.dawn(observer, date).replace(microsecond=0)
            result_dict["dawn_utc"] = dawn_utc.replace(tzinfo=None)
            result_dict["dawn_local"] = dawn_utc.astimezone().time()
        except Exception as e:
            result_dict["dawn_comment"] = e
        try:
            sunrise_utc = astral.sun.sunrise(observer, date).replace(microsecond=0)
            result_dict["sunrise_utc"] = sunrise_utc.replace(tzinfo=None)
            result_dict["sunrise_local"] = sunrise_utc.astimezone().time()
        except Exception as e:
            result_dict["sunrise_comment"] = e
        try:
            sunset_utc = astral.sun.sunset(observer, date).replace(microsecond=0)
            result_dict["sunset_utc"] = sunset_utc.replace(tzinfo=None)
            result_dict["sunset_local"] = sunset_utc.astimezone().time()
        except Exception as e:
            result_dict["sunset_comment"] = e
        try:
            dusk_utc = astral.sun.dusk(observer, date).replace(microsecond=0)
            result_dict["dusk_utc"] = dusk_utc.replace(tzinfo=None)
            result_dict["dusk_local"] = dusk_utc.astimezone().time()
        except Exception as e:
            result_dict["dusk_comment"] = e
        try:
            moonrise_utc = astral.moon.moonrise(observer, date).replace(microsecond=0)
            result_dict["moonrise_utc"] = moonrise_utc.replace(tzinfo=None)
            result_dict["moonrise_local"] = moonrise_utc.astimezone().time()
        except Exception as e:
            result_dict["moonrise_comment"] = e
        try:
            moonset_utc = astral.moon.moonset(observer, date).replace(microsecond=0)
            result_dict["moonset_utc"] = moonset_utc.replace(tzinfo=None)
            result_dict["moonset_local"] = moonset_utc.astimezone().time()
        except Exception as e:
            result_dict["moonset_comment"] = e
        try:
            moon_phase_0to28 = 0.0
            moon_phase_0to28 = astral.moon.phase(date)
            result_dict["moon_phase_0to28"] = round(moon_phase_0to28, 2)
        except Exception as e:
            print("Exception: ", e)
        try:
            moon_phase = self.moon_phase_to_name(moon_phase_0to28, detailed=False)
            result_dict["moon_phase"] = moon_phase
        except Exception as e:
            print("Exception: ", e)
        try:
            moon_phase_detailed = self.moon_phase_to_name(
                moon_phase_0to28, detailed=True
            )
            result_dict["moon_phase_detailed"] = moon_phase_detailed
        except Exception as e:
            print("Exception: ", e)

        # Add to memory cache.
        self.memory_cache_dict[cache_key] = result_dict

        return result_dict

    def moon_phase_to_name(self, moon_phase, detailed=True):
        """ """
        phase_name = ""
        if detailed:
            delta = 1.75
            if (moon_phase >= 0.00) and (moon_phase < 0.00 + delta):
                phase_name = "New moon"
            elif (moon_phase >= 3.50 - delta) and (moon_phase < 3.50 + delta):
                phase_name = "Waxing crescent"
            elif (moon_phase >= 7.00 - delta) and (moon_phase < 7.00 + delta):
                phase_name = "First quarter"
            elif (moon_phase >= 10.50 - delta) and (moon_phase < 10.50 + delta):
                phase_name = "Waxing gibbous"
            elif (moon_phase >= 14.00 - delta) and (moon_phase < 14.00 + delta):
                phase_name = "Full moon"
            elif (moon_phase >= 17.50 - delta) and (moon_phase < 17.50 + delta):
                phase_name = "Wanning gibbous"
            elif (moon_phase >= 21.00 - delta) and (moon_phase < 21.00 + delta):
                phase_name = "Last quarter"
            elif (moon_phase >= 24.50 - delta) and (moon_phase < 24.5 + delta):
                phase_name = "Wanning crescent"
            elif (moon_phase >= 28.00 - delta) and (moon_phase < 28.00):
                phase_name = "New moon"
        else:
            delta = 3.5
            if (moon_phase >= 0.00) and (moon_phase < 0.00 + delta):
                phase_name = "New moon"
            elif (moon_phase >= 7.00 - delta) and (moon_phase < 7.00 + delta):
                phase_name = "First quarter"
            elif (moon_phase >= 14.00 - delta) and (moon_phase < 14.00 + delta):
                phase_name = "Full moon"
            elif (moon_phase >= 21.00 - delta) and (moon_phase < 21.00 + delta):
                phase_name = "Last quarter"
            elif (moon_phase >= 28.00 - delta) and (moon_phase < 28.00):
                phase_name = "New moon"
        #
        return phase_name


# MAIN.
if __name__ == "__main__":
    """For test."""

    # latitude = 80.0
    # latitude = -80.0
    latitude = 50.0
    longitude = 15.0
    # date = datetime.date(2026, 1, 1)
    date = datetime.date(2026, 4, 15)
    # date = datetime.date(2026, 6, 1)
    # date = datetime.date(2026, 9, 1)

    sun_moon = SunMoon()
    result_dict = sun_moon.get_sun_moon_info(latitude, longitude, date)
    print("")
    print("latitude_dd :", str(result_dict.get("latitude_dd", "")))
    print("longitude_dd :", str(result_dict.get("longitude_dd", "")))
    print("date :", str(result_dict.get("date", "")))
    print("dawn_utc :", str(result_dict.get("dawn_utc", "")))
    print("sunrise_utc :", str(result_dict.get("sunrise_utc", "")))
    print("sunset_utc :", str(result_dict.get("sunset_utc", "")))
    print("dusk_utc :", str(result_dict.get("dusk_utc", "")))
    print("moonrise_utc :", str(result_dict.get("moonrise_utc", "")))
    print("moonset_utc :", str(result_dict.get("moonset_utc", "")))
    print("dawn_local :", str(result_dict.get("dawn_local", "")))
    print("sunrise_local :", str(result_dict.get("sunrise_local", "")))
    print("sunset_local :", str(result_dict.get("sunset_local", "")))
    print("dusk_local :", str(result_dict.get("dusk_local", "")))
    print("moonrise_local :", str(result_dict.get("moonrise_local", "")))
    print("moonset_local :", str(result_dict.get("moonset_local", "")))
    print("moon_phase_0to28 :", str(result_dict.get("moon_phase_0to28", "")))
    print("moon_phase :", str(result_dict.get("moon_phase", "")))
    print("moon_phase_detailed :", str(result_dict.get("moon_phase_detailed", "")))
    print("dawn_comment :", str(result_dict.get("dawn_comment", "")))
    print("sunrise_comment :", str(result_dict.get("sunrise_comment", "")))
    print("sunset_comment :", str(result_dict.get("sunset_comment", "")))
    print("dusk_comment :", str(result_dict.get("dusk_comment", "")))
    print("moonrise_comment :", str(result_dict.get("moonrise_comment", "")))
    print("moonset_comment :", str(result_dict.get("moonset_comment", "")))
    print("")

    # Test cache.
    result_dict = sun_moon.get_sun_moon_info(latitude, longitude, date)
    print("Cache-test: ", result_dict)
