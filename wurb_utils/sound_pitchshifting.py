#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import numpy
import scipy.signal
import scipy.interpolate
import logging


class SoundPitchShifting(object):
    """
    For audio feedback by using Pitch shifting.
    Simple time domain implementation by using overlapped
    windows and the Kaiser window function.
    """

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.queue = None
        self.clear()

    def clear(self):
        """ """
        self.channels = None
        self.sampling_freq_in = None
        self.sampling_freq_out = None
        self.volume = None
        self.pitch_div_factor = None
        self.time_exp_freq = None
        self.hop_out_length = None
        self.hop_in_length = None
        self.resample_factor = None
        self.kaiser_beta = None
        self.window_size = None
        self.filter_order = 10
        # Work buffers.
        self.insert_pos = 0
        self.work_in = None
        self.work_out = None
        self.work_in_left = None
        self.work_out_left = None
        self.work_in_right = None
        self.work_out_right = None

    def setup(
        self,
        channels,
        sampling_freq_in,
        sampling_freq_out,
        pitch_factor,
        volume_percent,
        filter_low_khz,
        filter_high_khz,
        overlap_factor,
        in_queue_length,
    ):
        """ """
        self.channels = channels
        self.sampling_freq_in = int(sampling_freq_in)
        self.sampling_freq_out = int(sampling_freq_out)
        pitch_factor = int(pitch_factor)
        volume = int(volume_percent)
        filter_low_khz = filter_low_khz
        filter_high_khz = filter_high_khz
        self.pitch_div_factor = int(float(pitch_factor))
        # self.volume = float((float(volume) / 100.0) * 10.0)
        self.volume = float((float(volume) / 100.0) * 1.0)
        self.filter_low_limit_hz = int(float(filter_low_khz) * 1000.0)
        self.filter_high_limit_hz = int(float(filter_high_khz) * 1000.0)
        self.overlap_factor = overlap_factor
        # Setup queue for data in.
        self.queue = asyncio.Queue(maxsize=in_queue_length)
        # List of out data queues.
        self.out_queue_list = []

        self.calc_params()

    def get_queue(self):
        """ """
        return self.queue

    def add_out_queue(self, out_queue):
        """ """
        self.out_queue_list.append(out_queue)

    def calc_params(self):
        """ """
        try:
            # self.channels = self.config["channels"]
            # self.sampling_freq_in = int(self.config["sampling_freq_in_hz"])
            # self.sampling_freq_out = int(self.config["sampling_freq_out_hz"])
            # Volume and pitch.
            # volume = int(self.config["volume_percent"])
            # self.volume = float((float(volume) / 100.0) * 10.0)
            # pitch_factor = int(self.config["pitch_factor"])
            # self.pitch_div_factor = int(float(pitch_factor))
            # Filter.
            # filter_low_khz = self.config["filter_low_khz"]
            # filter_high_khz = self.config["filter_high_khz"]
            # self.filter_low_limit_hz = int(float(filter_low_khz) * 1000.0)
            # self.filter_high_limit_hz = int(float(filter_high_khz) * 1000.0)
            # Calculated parameters.
            self.time_exp_freq = int(self.sampling_freq_in / self.pitch_div_factor)
            self.hop_out_length = int(
                self.sampling_freq_in / 1000 / self.pitch_div_factor
            )
            self.hop_in_length = int(self.hop_out_length * self.pitch_div_factor)
            self.resample_factor = self.time_exp_freq / self.sampling_freq_out
            # Buffers.
            buffer_in_overlap_factor = float(self.overlap_factor)
            kaiser_beta = int(self.pitch_div_factor * 0.8)
            self.window_size = int(self.hop_in_length * buffer_in_overlap_factor)
            self.window_function = numpy.kaiser(self.window_size, beta=kaiser_beta)
            #
            # Reset work buffers.
            self.insert_pos = 0
            self.work_in = None
            self.work_out = None
            self.work_in_left = None
            self.work_out_left = None
            self.work_in_right = None
            self.work_out_right = None

            # For debug.
            self.logger.debug("PitchShifting - freq_in: " + str(self.sampling_freq_in))
            self.logger.debug(
                "PitchShifting - freq_out: " + str(self.sampling_freq_out)
            )
            self.logger.debug("PitchShifting - volume: " + str(self.volume))
            self.logger.debug(
                "PitchShifting - pitch_factor: " + str(self.pitch_div_factor)
            )
            self.logger.debug(
                "PitchShifting - time_exp_freq: " + str(self.time_exp_freq)
            )
            self.logger.debug(
                "PitchShifting - hop_out_length: " + str(self.hop_out_length)
            )
            self.logger.debug(
                "PitchShifting - hop_in_length: " + str(self.hop_in_length)
            )
            self.logger.debug(
                "PitchShifting - resample_factor: " + str(self.resample_factor)
            )
            self.logger.debug("PitchShifting - kaiser_beta: " + str(kaiser_beta))
            self.logger.debug("PitchShifting - window_size: " + str(self.window_size))

        except Exception as e:
            self.logger.error("PitchShifting - calc_params: " + str(e))

    async def start(self):
        """ """
        try:
            self.pitchshift_active = True

            await self.run_pitchshift()

            # # Run in executor.
            # self.main_loop = asyncio.get_event_loop()
            # self.pitchshift_executor = self.main_loop.run_in_executor(None, self.run_pitchshift)
        except Exception as e:
            message = "SoundPitchShifting - start. Exception: " + str(e)
            self.logger.debug(message)

    async def stop(self):
        """ """
        try:
            self.pitchshift_active = False
            if self.pitchshift_executor != None:
                self.pitchshift_executor.cancel()
                self.pitchshift_executor = None
        except Exception as e:
            message = "SoundPitchShifting - stop. Exception: " + str(e)
            self.logger.debug(message)

    async def run_pitchshift(self):
        """ """
        try:
            # Clear queue.
            while not self.queue.empty():
                self.queue.get_nowait()
                self.queue.task_done()
            # Copy data from queue to buffer.
            while self.pitchshift_active:
                try:
                    data_dict = await self.queue.get()
                    if "data" in data_dict:
                        await self.add_buffer(data_dict["data"])
                except asyncio.CancelledError:
                    self.logger.debug("PitchShifting - Was cancelled.")
                    break
                except Exception as e:
                    message = "PitchShifting - Failed to read queue: " + str(e)
                    self.logger.debug(message)
        except Exception as e:
            message = "SoundPitchShifting - run_pitchshift. Exception: " + str(e)
            self.logger.debug(message)

    def create_buffers(self):
        """Create missing buffers."""
        if self.channels == "STEREO":
            # Left buffers.
            if self.work_in_left is None:
                self.work_in_left = numpy.array([], dtype=numpy.float32)
                # 3 sec pitchshifting buffer length.
                pitchshifting_buffer_length = int(self.sampling_freq_out * 3)
                self.work_out_left = numpy.zeros(
                    pitchshifting_buffer_length, dtype=numpy.float32
                )
                self.insert_pos = 0
            # Right buffers.
            if self.work_in_right is None:
                self.work_in_right = numpy.array([], dtype=numpy.float32)
                # 3 sec pitchshifting buffer length.
                pitchshifting_buffer_length = int(self.sampling_freq_out * 3)
                self.work_out_right = numpy.zeros(
                    pitchshifting_buffer_length, dtype=numpy.float32
                )
                self.insert_pos = 0
        else:
            # Mono buffers.
            if self.work_in is None:
                self.work_in = numpy.array([], dtype=numpy.float32)
                # 3 sec pitchshifting buffer length.
                pitchshifting_buffer_length = int(self.sampling_freq_out * 3)
                self.work_out = numpy.zeros(
                    pitchshifting_buffer_length, dtype=numpy.float32
                )
                self.insert_pos = 0

    async def add_buffer(self, buffer_int16):
        """ """
        try:
            # Create missing buffers.
            self.create_buffers()

            if self.channels.upper() == "STEREO":
                result_buffer = self.calc_pithshifting_stereo(buffer_int16)
            else:
                result_buffer = self.calc_pithshifting_mono(buffer_int16)
            #
            if len(result_buffer) > 0:
                self.buffer_to_queues(result_buffer)
        except Exception as e:
            message = "SoundPitchShifting - add_buffer. Exception: " + str(e)
            self.logger.debug(message)

    def calc_pithshifting_stereo(self, buffer_int16):
        """ """
        try:
            # Buffer delivered as int16. Transform to interval -1 to 1.
            buffer = buffer_int16 / 32768.0

            # Check sound level. Reduce if necessary to avoid clipping.
            max_value = buffer.max() * self.volume + 0.05
            if max_value > 1.0:
                buffer = buffer / max_value

            # Separate left and right channels.
            left_buffer = buffer[::2].copy()
            right_buffer = buffer[1::2].copy()

            # Filter buffer. Butterworth bandpass.
            filtered_left = self.butterworth_filter(left_buffer)
            filtered_right = self.butterworth_filter(right_buffer)

            # Concatenate with old buffer.
            self.work_in_left = numpy.concatenate((self.work_in_left, filtered_left))
            self.work_in_right = numpy.concatenate((self.work_in_right, filtered_right))

            # Add overlaps on pitchshifting_buffer. Window function is applied on "part".
            self.insert_pos = 0
            while self.work_in_left.size > self.window_size:
                part_left = self.work_in_left[: self.window_size] * self.window_function
                part_right = (
                    self.work_in_right[: self.window_size] * self.window_function
                )
                self.work_in_left = self.work_in_left[self.hop_in_length :]
                self.work_in_right = self.work_in_right[self.hop_in_length :]
                self.work_out_left[
                    self.insert_pos : self.insert_pos + self.window_size
                ] += part_left
                self.work_out_right[
                    self.insert_pos : self.insert_pos + self.window_size
                ] += part_right
                self.insert_pos += self.hop_out_length

            # Flush.
            new_part_left = self.work_out_left[: self.insert_pos].copy()
            self.work_out_left[: self.window_size] = self.work_out_left[
                self.insert_pos : self.insert_pos + self.window_size
            ]
            self.work_out_left[self.window_size :] = 0.0

            new_part_right = self.work_out_right[: self.insert_pos].copy()
            self.work_out_right[: self.window_size] = self.work_out_right[
                self.insert_pos : self.insert_pos + self.window_size
            ]
            self.work_out_right[self.window_size :] = 0.0

            # Resample.
            new_part_left_2 = self.resample(new_part_left)
            new_part_right_2 = self.resample(new_part_right)

            # Join left and right to stereo.
            left_result = new_part_left_2.reshape(-1, 1)
            right_result = new_part_right_2.reshape(-1, 1)
            stereo_buffer = numpy.hstack((left_result, right_result))
            stereo_buffer_2 = stereo_buffer.reshape(-1)

            # Buffer to return. Convert to int16 and set volume.
            new_buffer_int16 = numpy.array(
                stereo_buffer_2 * 32768.0 * self.volume, dtype=numpy.int16
            )

            return new_buffer_int16

        except Exception as e:
            self.logger.debug(
                "PitchShifting - Exception in calc_pithshifting_stereo: " + str(e)
            )

        return None

    def calc_pithshifting_mono(self, buffer_int16):
        """ """
        try:
            # Buffer delivered as int16. Transform to intervall -1 to 1.
            buffer = buffer_int16 / 32768.0

            # Check sound level. Reduce if necessary to avoid clipping.
            max_value = buffer.max() * self.volume + 0.20
            if max_value > 1.0:
                buffer = buffer / max_value
                print("MAX VALUE: " + str(max_value - 0.20))

            # Filter buffer. Butterworth bandpass.
            filtered = self.butterworth_filter(buffer)

            # Concatenate with old buffer.
            self.work_in = numpy.concatenate((self.work_in, filtered))

            # Add overlaps on pitchshifting_buffer. Window function is applied on "part".
            self.insert_pos = 0
            while self.work_in.size > self.window_size:
                part = self.work_in[: self.window_size] * self.window_function
                self.work_in = self.work_in[self.hop_in_length :]
                self.work_out[
                    self.insert_pos : self.insert_pos + self.window_size
                ] += part
                self.insert_pos += self.hop_out_length

            # Flush.
            new_part = self.work_out[: self.insert_pos].copy()
            self.work_out[: self.window_size] = self.work_out[
                self.insert_pos : self.insert_pos + self.window_size
            ]
            self.work_out[self.window_size :] = 0.0

            # Resample.
            new_part_2 = self.resample(new_part)

            # Buffer to return. Convert to int16 and set volume.
            new_buffer_int16 = numpy.array(
                new_part_2 * 32768.0 * self.volume, dtype=numpy.int16
            )

            return new_buffer_int16

        except Exception as e:
            self.logger.debug(
                "PitchShifting - Exception in calc_pithshifting_mono: " + str(e)
            )

        return None

    def buffer_to_queues(self, buffer_int16):
        """ """
        try:
            # Put data on queues in the queue list.
            for data_queue in self.out_queue_list:
                # Copy data.
                data_int16_copy = buffer_int16.copy()
                # Put together.
                data_dict = {
                    "status": "data",
                    "data": data_int16_copy,
                }
                try:
                    # if not data_queue.full():
                    #     self.main_loop.call_soon_threadsafe(
                    #         data_queue.put_nowait, data_dict
                    #     )
                    if not data_queue.full():
                        data_queue.put_nowait(data_dict)
                    else:
                        self.logger.debug("PitchShifting - Queue full.")
                #
                except Exception as e:
                    message = "PitchShifting - Failed to put data on queue: " + str(e)
                    self.logger.error(message)
                    if not self.main_loop.is_running():
                        # Terminate.
                        self.capture_active = False
                        break
        except Exception as e:
            self.logger.debug(
                "PitchShifting - Exception in buffer_to_queues: " + str(e)
            )

    def butterworth_filter(self, buffer):
        # Filter buffer. Butterworth bandpass.
        filtered = buffer
        try:
            low_limit_hz = self.filter_low_limit_hz
            high_limit_hz = self.filter_high_limit_hz
            if (high_limit_hz + 100) >= (self.sampling_freq_in / 2):
                high_limit_hz = self.sampling_freq_in / 2 - 100
            if low_limit_hz < 0 or (low_limit_hz + 100 >= high_limit_hz):
                low_limit_hz = 100
            sos = scipy.signal.butter(
                self.filter_order,
                [low_limit_hz, high_limit_hz],
                btype="bandpass",
                fs=self.sampling_freq_in,
                output="sos",
            )
            filtered = scipy.signal.sosfilt(sos, buffer)
        except Exception as e:
            pass
            self.logger.debug(
                "PitchShifting - Exception in butterworth_filter: " + str(e)
            )

        return filtered

    def resample(self, x, kind="linear"):
        """Resample to 48000 Hz, in most cases, to match output devices."""
        if x.size > 0:
            n = int(numpy.ceil(x.size / self.resample_factor))
            f = scipy.interpolate.interp1d(numpy.linspace(0, 1, x.size), x, kind)
            return f(numpy.linspace(0, 1, n))
        else:
            return x
