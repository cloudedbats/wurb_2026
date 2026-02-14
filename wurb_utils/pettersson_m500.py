#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Copyright (c) 2020-present Arnold Andreasson
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import time
import numpy
import logging
import platform

from wurb_utils import pettersson_m500_batmic


class PetterssonM500:
    """ """

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.clear()
        # USB driver for M500. Only on Linux.
        self.pettersson_m500 = None
        if platform.system() == "Linux":
            self.pettersson_m500 = pettersson_m500_batmic.PetterssonM500BatMic()
            self.pettersson_m500.stop_stream()
            self.pettersson_m500.reset()

    def clear(self):
        # Specific for M500.
        self.device_index = 9999
        self.device_name = "Pettersson M500 (500kHz)"
        self.channels = 1
        self.config_channels = "MONO"
        self.sampling_freq_hz = 500000
        #
        self.frames_per_buffer = None
        self.buffer_size = None
        #
        self.out_queue_list = []
        self.main_loop = None
        self.capture_executor = None
        self.capture_is_running = False
        self.capture_is_active = False

    def is_m500_available(self):
        """ """
        if self.pettersson_m500 == None:
            return False
        #
        return self.pettersson_m500.is_available()


    def is_capture_running(self):
        """ """
        return self.capture_is_running

    def get_selected_capture_device(self):
        """ """
        info_dict = {}
        info_dict["device_index"] = None
        info_dict["device_name"] = self.device_name
        info_dict["input_channels"] = self.channels
        info_dict["config_channels"] = self.channels
        info_dict["sampling_freq_hz"] = self.sampling_freq_hz
        return info_dict

    def setup(
        self,
        device_index,
        device_name,
        channels,
        config_channels,
        sampling_freq_hz,
        frames_per_buffer,
        buffer_size,
    ):
        """ """
        # Should not be changed.
        # self.device_index = device_index
        # self.device_name = device_name
        # self.channels = channels
        # self.config_channels = config_channels
        # self.sampling_freq_hz = sampling_freq_hz
        self.frames_per_buffer = frames_per_buffer
        self.buffer_size = buffer_size

    def add_out_queue(self, out_queue):
        """ """
        self.out_queue_list.append(out_queue)

    async def start(self):
        """ """
        try:
            while self.capture_is_running == True:
                self.logger.debug(
                    "PetterssonM500 - Start: Capture is running, waiting 2 sec... "
                )
                await asyncio.sleep(2.0)

            # Use executor for the IO-blocking part.
            self.main_loop = asyncio.get_event_loop()
            self.capture_executor = self.main_loop.run_in_executor(
                None, self.run_capture
            )
        except Exception as e:
            message = "PetterssonM500 - start. Exception: " + str(e)
            self.logger.debug(message)

    async def stop(self):
        """ """
        if self.pettersson_m500 == None:
            return
        try:
            self.capture_is_active = False
            self.pettersson_m500.stop_stream()
            self.pettersson_m500.reset()
            if self.capture_executor != None:
                self.capture_executor.cancel()
                self.capture_executor = None
        except Exception as e:
            message = "PetterssonM500 - stop. Exception: " + str(e)
            self.logger.debug(message)

    def run_capture(self):
        """ """
        if self.pettersson_m500 == None:
            return
        try:
            self.stream_time_s = time.time()
            self.pettersson_m500.start_stream()
            self.pettersson_m500.led_on()
        except Exception as e:
            # Logging error.
            message = "Failed to create stream (M500): " + str(e)
            self.logger.debug(message)
            return

        pmc_capture = None
        self.capture_is_active = True
        try:
            self.logger.debug("PetterssonM500 - Sound capture started.")
            # Empty buffer.
            data = self.pettersson_m500.read_stream()
            # Prepare.
            self.capture_is_running = True
            # Time related.
            calculated_time_s = time.time()
            time_increment_s = self.buffer_size / self.sampling_freq_hz
            # Empty numpy buffer.
            in_buffer_int16 = numpy.array([], dtype=numpy.int16)
            # Loop.
            while self.capture_is_active:
                # Read from capture device.
                data = self.pettersson_m500.read_stream()
                if len(data) > 0:
                    # Convert from string-byte array to int16 array.
                    in_data_int16 = numpy.frombuffer(data, dtype=numpy.int16)
                    # Concatenate
                    in_buffer_int16 = numpy.concatenate(
                        (in_buffer_int16, in_data_int16)
                    )
                    while len(in_buffer_int16) >= self.buffer_size:
                        # Copy "buffer_size" part and save remaining part.
                        data_int16 = in_buffer_int16[0 : self.buffer_size]
                        in_buffer_int16 = in_buffer_int16[self.buffer_size :]

                        # Put data on queues in the queue list.
                        for data_queue in self.out_queue_list:
                            # Time rounded to half sec.
                            calculated_time_s += time_increment_s
                            device_time = int((calculated_time_s) * 2) / 2
                            # Used to detect time drift.
                            detector_time = time.time()
                            # Copy data.
                            data_int16_copy = data_int16.copy()
                            # Put together.
                            data_dict = {
                                "status": "data",
                                "adc_time": device_time,
                                "detector_time": detector_time,
                                "data": data_int16_copy,
                            }
                            try:
                                if not data_queue.full():
                                    self.main_loop.call_soon_threadsafe(
                                        data_queue.put_nowait, data_dict
                                    )
                                else:
                                    self.logger.debug("PetterssonM500 - Queue full.")
                            #
                            except Exception as e:
                                message = (
                                    "PetterssonM500 - Failed to put on queue: " + str(e)
                                )
                                self.logger.debug(message)
                                if not self.main_loop.is_running():
                                    # Terminate.
                                    self.capture_is_active = False
                                    break
        #
        except asyncio.CancelledError:
            self.logger.debug("PetterssonM500 - Was cancelled.")
        except Exception as e:
            message = "PetterssonM500 - run_capture. Exception: " + str(e)
            self.logger.debug(message)
        finally:
            self.logger.debug("PetterssonM500 - Capture ended.")
            self.capture_is_active = False
            if pmc_capture:
                pmc_capture.close()
            #
            self.pettersson_m500.stop_stream()
            self.pettersson_m500.reset()
            #
            self.capture_is_running = False
