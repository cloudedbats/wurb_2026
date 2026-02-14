#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
# import serial_asyncio
import serial_asyncio_fast
import serial.tools.list_ports
import logging
import pathlib
import datetime
import platform

import wurb_core


class GpsReader(object):
    """GPS reader for USB GPS Receiver."""

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
        self.latlong_event = None
        #
        self.gps_datetime_utc = None
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0
        self.first_gps_time_received = False
        self.first_gps_time_counter = 30
        self.last_used_lat_dd = 0.0
        self.last_used_long_dd = 0.0
        #
        self.gps_control_task = None
        self.serial_coro = None
        self.serial_transport = None
        self.serial_protocol = None
        #
        self.is_gps_quality_ok = False
        self.number_of_satellites = 0

    def configure(self):
        """ """
        config = self.config
        self.min_number_of_satellites = config.get(
            "gps_reader.min_number_of_satellites", 3
        )
        self.adjust_detector_time = config.get("gps_reader.adjust_detector_time", False)
        self.max_time_diff_s = config.get(
            "gps_reader.accepted_detector_time_diff_s", 60
        )
        self.gps_loop_sleep_s = config.get("gps_reader.gps_loop_sleep_s", 20)
        self.gps_device_whitelist = config.get(
            "gps_reader.gps_device_whitelist", ["1546:01A8", "067B:2303"]
        )

    def startup(self):
        """ """
        self.first_gps_time_received = False
        self.first_gps_time_counter = 30
        self.last_used_lat_dd = 0.0
        self.last_used_long_dd = 0.0
        self.number_of_satellites = 0

        # asyncio.run_coroutine_threadsafe(self.gps_control_loop(), asyncio.get_event_loop())
        self.gps_control_task = asyncio.create_task(
            self.gps_control_loop(), name="GPS control loop"
        )

    def shutdown(self):
        """ """
        self.stop()
        if self.gps_control_task != None:
            self.gps_control_task.cancel()
            self.gps_control_task = None

    async def gps_control_loop(self):
        """ """
        try:
            self.is_gps_quality_ok = False
            while True:
                try:
                    await self.start()
                    await asyncio.sleep(self.gps_loop_sleep_s)
                    self.stop()
                except asyncio.CancelledError:
                    self.logger.debug("GPS control was cancelled.")
                    break
        except Exception as e:
            message = "GpsReader - gps_control_loop. Exception: " + str(e)
            self.logger.debug(message)

    async def get_datetime_utc(self):
        """ """
        try:
            if self.gps_datetime_utc:
                utc_datetime = self.gps_datetime_utc.replace(
                    tzinfo=datetime.timezone.utc
                )
                return utc_datetime
            #
            return None
        except Exception as e:
            message = "GpsReader - get_datetime_utc. Exception: " + str(e)
            self.logger.debug(message)
            return None

    async def get_datetime_local(self):
        """ """
        try:
            if self.gps_datetime_utc:
                local_datetime = self.gps_datetime_utc.replace(
                    tzinfo=datetime.timezone.utc
                ).astimezone(tz=None)
                return local_datetime
            #
            return None
        except Exception as e:
            message = "GpsReader - get_datetime_local. Exception: " + str(e)
            self.logger.debug(message)
            return None

    def get_latlong_event(self):
        """Used for synchronization."""
        if self.latlong_event == None:
            self.latlong_event = asyncio.Event()
        return self.latlong_event

    def trigger_latlong_event(self):
        """Used for synchronization."""
        # Create a new event and release the old.
        old_event = self.get_latlong_event()
        self.latlong_event = asyncio.Event()
        old_event.set()

    def get_latitude_longitude(self):
        """ """
        # return (self.gps_latitude, self.gps_longitude)
        return (self.last_used_lat_dd, self.last_used_long_dd)

    def get_number_of_satellites(self):
        """ """
        return self.number_of_satellites

    async def start(self):
        """ """
        try:
            # Check if USB GPS is connected.
            gps_device_path_found = None
            for info in serial.tools.list_ports.comports():
                if gps_device_path_found != None:
                    break
                id_string = "Device: " + info.device + " HWID: " + info.hwid
                # print(id_string)

                for whitelist_item in self.gps_device_whitelist:
                    if whitelist_item.upper() in id_string.upper():
                        gps_device = pathlib.Path(info.device)
                        if gps_device.exists():
                            gps_device_path_found = str(gps_device)
                            break

            # Read serial, if connected.
            if gps_device_path_found:
                # self.serial_coro = serial_asyncio.create_serial_connection(
                self.serial_coro = serial_asyncio_fast.create_serial_connection(
                    asyncio.get_event_loop(),
                    ReadGpsSerialNmea,
                    gps_device_path_found,  # For example "/dev/ttyACM0".
                    baudrate=4800,  # 9600, 19200, 38400
                )
                # Start. Serial_protocol is instance of ReadGpsSerialNmea
                self.serial_transport, self.serial_protocol = await self.serial_coro
                # To be used for calls back to master.
                self.serial_protocol.gps_manager = self
            else:
                # GPS device not found.
                self.is_gps_quality_ok = False
                self.number_of_satellites = 0
                if (self.last_used_lat_dd != 0.0) or (self.last_used_long_dd != 0.0):
                    self.last_used_lat_dd = 0.0
                    self.last_used_long_dd = 0.0
                    self.trigger_latlong_event()
        except Exception as e:
            message = "GpsReader - start. Exception: " + str(e)
            self.logger.debug(message)

    def stop(self):
        """ """
        if self.serial_coro:
            if self.serial_transport:
                self.serial_transport.close()

    def parse_nmea(self, data):
        """
        From NMEA documentation:

        RMC - NMEA has its own version of essential gps pvt
        (position, velocity, time) data. It is called RMC,
        The Recommended Minimum, which will look similar to:
        $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
        Where:
            RMC          Recommended Minimum sentence C
            123519       Fix taken at 12:35:19 UTC
            A            Status A=active or V=Void.
            4807.038,N   Latitude 48 deg 07.038' N
            01131.000,E  Longitude 11 deg 31.000' E
            022.4        Speed over the ground in knots
            084.4        Track angle in degrees True
            230394       Date - 23rd of March 1994
            003.1,W      Magnetic Variation
            *6A          The checksum data, always begins with *

        Example from test (Navilock NL-602U):
            $GPRMC,181841.000,A,5739.7158,N,01238.3515,E,0.52,289.92,040620,,,A*6D
        """
        parts = data.split(",")
        # print("GPS data: ", data)

        # GPGGA. Check quality.
        if (len(parts) >= 8) and (len(parts[0]) >= 6) and (parts[0][3:6] == "GGA"):
            if parts[6] == "0":
                # Fix quality 0 = invalid.
                self.is_gps_quality_ok = False
                return
            number_of_satellites = parts[7]
            self.number_of_satellites = number_of_satellites
            if int(number_of_satellites) < self.min_number_of_satellites:
                # More satellites needed.
                self.is_gps_quality_ok = False
                return
            # Seems to be ok.
            self.is_gps_quality_ok = True
            return

        # GPRMC. Get date, time and lat/long.
        if (len(parts) >= 8) and (len(parts[0]) >= 6) and (parts[0][3:6] == "RMC"):
            if self.is_gps_quality_ok == False:
                return

            latitude_dd = 0.0
            longitude_dd = 0.0

            if (len(data) >= 50) and (len(parts) >= 8):
                time = parts[1]
                _gps_status = parts[2]
                latitude = parts[3]
                lat_n_s = parts[4]
                longitude = parts[5]
                long_w_e = parts[6]
                date = parts[9]
            else:
                if (self.last_used_lat_dd != 0.0) or (self.last_used_long_dd != 0.0):
                    self.last_used_lat_dd = 0.0
                    self.last_used_long_dd = 0.0
                    self.trigger_latlong_event()
                #
                self.number_of_satellites = 0
                return

            # Extract date and time.
            datetime_utc = datetime.datetime(
                int("20" + date[4:6]),
                int(date[2:4]),
                int(date[0:2]),
                int(time[0:2]),
                int(time[2:4]),
                int(time[4:6]),
            )
            # Extract latitude and longitude.
            latitude_dd = round(
                float(latitude[0:2]) + (float(latitude[2:].strip()) / 60.0), 5
            )
            if lat_n_s == "S":
                latitude_dd *= -1.0
            longitude_dd = round(
                float(longitude[0:3]) + (float(longitude[3:].strip()) / 60.0), 5
            )
            if long_w_e == "W":
                longitude_dd *= -1.0

            self.gps_datetime_utc = datetime_utc
            self.gps_latitude = latitude_dd
            self.gps_longitude = longitude_dd

            # Check if detector time should be set.
            # Don't do this for desktop apps on Windows and macOS.
            if platform.system() in ["Linux"]:
                try:
                    if not self.first_gps_time_received:
                        # Wait for GPS to stabilize.
                        self.first_gps_time_counter -= 1
                        if self.first_gps_time_counter <= 0:
                            if self.gps_datetime_utc:
                                if self.is_time_valid(self.gps_datetime_utc):
                                    self.first_gps_time_received = True
                                    # Set detector unit time.
                                    gps_local_time = self.gps_datetime_utc.replace(
                                        tzinfo=datetime.timezone.utc
                                    ).astimezone()
                                    gps_local_timestamp = gps_local_time.timestamp()

                                    # Connect to main loop.
                                    asyncio.run_coroutine_threadsafe(
                                        wurb_core.wurb_rpi.set_detector_time(
                                            gps_local_timestamp,
                                            cmd_source="from GPS",
                                        ),
                                        asyncio.get_event_loop(),
                                    )
                    else:
                        # Compare detector time and GPS time.
                        datetime_utc = datetime.datetime.now(datetime.UTC)
                        diff = self.gps_datetime_utc - datetime_utc
                        diff_in_s = diff.total_seconds()
                        if abs(diff_in_s) > self.max_time_diff_s:
                            # Set detector unit time.
                            gps_local_time = self.gps_datetime_utc.replace(
                                tzinfo=datetime.timezone.utc
                            ).astimezone()
                            gps_local_timestamp = gps_local_time.timestamp()
                            # Connect to main loop.
                            asyncio.run_coroutine_threadsafe(
                                wurb_core.wurb_rpi.set_detector_time(
                                    gps_local_timestamp, cmd_source="from GPS"
                                ),
                                asyncio.get_event_loop(),
                            )
                except Exception as e:
                    message = "GpsReader - parse_nmea. Exception: " + str(e)
                    self.logger.debug(message)

            # Check if lat/long changed.
            lat_dd = round(self.gps_latitude, 5)
            long_dd = round(self.gps_longitude, 5)
            if (self.last_used_lat_dd != lat_dd) or (self.last_used_long_dd != long_dd):
                # Changed.
                self.last_used_lat_dd = lat_dd
                self.last_used_long_dd = long_dd
                self.trigger_latlong_event()

            # print("GPS datetime: ", datetime_utc)
            # print("GPS latitude: ", latitude_dd)
            # print("GPS longitude: ", longitude_dd)

    def is_time_valid(self, gps_time):
        """To avoid strange datetime (like 1970-01-01 or 2038-01-19) from some GPS units."""
        try:
            gps_utc = gps_time.astimezone(tz=datetime.timezone.utc)
            # gps_utc = parser.parse(gps_time)
            datetime_now = datetime.datetime.now(datetime.timezone.utc)
            if gps_utc < (datetime_now - datetime.timedelta(days=2)):
                return False
            elif gps_utc > (datetime_now + datetime.timedelta(days=(365 * 5))):
                return False
            else:
                return True
        except Exception as e:
            message = "GpsReader - is_time_valid. Exception: " + str(e)
            self.logger.debug(message)
        return False


class ReadGpsSerialNmea(asyncio.Protocol):
    """Serial connection for serial_asyncio/serial_asyncio_fast."""

    def __init__(self):
        """ """
        super().__init__()
        self.buf = bytes()
        self.gps_manager = None

    def connection_made(self, transport):
        transport.serial.rts = False
        # self.gps_manager: GPS manager for callbacks will be set externally.
        # print("GPS: Connection made.")

    def data_received(self, data):
        try:
            # print("Data: ", data)
            # Avoid problems with data streams without new lines.
            if len(self.buf) >= 1000:
                self.buf = bytes()
            #
            self.buf += data
            if b"\n" in self.buf:
                rows = self.buf.split(b"\n")
                self.buf = rows[-1]  # Save remaining part.
                for row in rows[:-1]:
                    row = row.decode().strip()
                    if (row.find("RMC,") > 0) or (row.find("GGA,") > 0):
                        # print("NMEA: ", row)
                        if self.gps_manager:
                            self.gps_manager.parse_nmea(row)
        except Exception as e:
            message = "GpsReader - data_received. Exception: " + str(e)
            # self.logger.debug(message)
            print(message)

    def connection_lost(self, exc):
        pass
        # # Logging debug.
        # if self.gps_manager:
        #     message = "GPS:ReadGpsSerialNmea: connection_lost."
        # #     self.logger.debug(message)
        #     print(message)
