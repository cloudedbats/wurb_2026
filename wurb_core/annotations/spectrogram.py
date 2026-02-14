#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wurb_2026
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import pathlib
import logging
import matplotlib
import matplotlib.figure
from scipy import signal
from scipy.io import wavfile
import numpy

# import base64
import pybase64  # Is faster.
from io import BytesIO


class SpectrogramCreator(object):

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
        self.is_running = False
        self.sampling_freq_in = None
        self.volume = None
        self.pitch_div_factor = None
        self.time_exp_freq = None
        self.hop_out_length = None
        self.hop_in_length = None
        self.kaiser_beta = None
        self.window_size = None

    def configure(self):
        """ """

    def create_spectrogram(self, source_path):
        """ """
        if self.is_running is True:
            message = "SpectrogramCreator - Not executed, already running. "
            self.logger.debug(message)
            return None

        try:
            self.is_running = True

            matplotlib.rcParams.update({"font.size": 6})
            figure = matplotlib.figure.Figure(
                figsize=(9, 3),
                dpi=150,
            )
            ax1 = figure.add_subplot(111)

            try:
                sample_rate, samples = wavfile.read(source_path)
                # Change from time expanded, TE, to full scan, FS.
                if sample_rate < 90000:
                    sample_rate *= 10

                # start_ix = int(sample_rate * 4.7)
                # end_ix = int(sample_rate * 4.9)
                # start_ix = int(sample_rate * 2.0)
                # end_ix = int(sample_rate * 2.5)

                # Reduce number of samples by using pitch shifting.
                pitch_factor = 10
                self.setup_pitchshifting(
                    sampling_freq_in=sample_rate, pitch_factor=pitch_factor
                )
                ps_samples = self.calc_pitchshifting_mono(samples)
                sample_rate = int(sample_rate / pitch_factor)
                if ps_samples is None:
                    return None

                # wavfile.write("test_pitch.wav", sample_rate, ps_samples)

                # Calculate spectrogram.
                frequencies, times, spectrogram = signal.spectrogram(
                    ps_samples,
                    # samples[start_ix:end_ix],
                    sample_rate,
                    window="blackmanharris",
                    # nperseg=256,
                    # noverlap=192,
                    nperseg=512,
                    noverlap=384,
                )
                # From Hz to kHz.
                # frequencies = frequencies / 1000.0
                frequencies = frequencies / 100.0

                # Fix colors, use logarithmic scale.
                for row in spectrogram:
                    row[row < 0.0002] = None

                ax1.grid(False)
                spectrogram_log10 = numpy.log10(spectrogram)
                ax1.pcolormesh(times, frequencies, spectrogram_log10, cmap="YlOrBr")

                # Title and labels.
                plot_title = str(pathlib.Path(source_path).name)
                ax1.set_title("File: " + plot_title, fontsize=8)
                # Axes.
                ax1.set_ylabel("Frequency (kHz)")
                ax1.set_xlabel("Time (s)")
                ax1.set_ylim((0, 120))
                # Grid.
                ax1.minorticks_on()
                ax1.grid(which="major", linestyle="-", linewidth="0.5", alpha=0.7)
                ax1.grid(which="minor", linestyle="-", linewidth="0.5", alpha=0.3)
                ax1.tick_params(
                    which="both", top="off", left="off", right="off", bottom="off"
                )

                # Save to a temporary buffer. Usage example:
                # "<img src='data:image/png;base64,{buffer}'/>"
                figure.tight_layout()
                buf = BytesIO()

                # name = pathlib.Path(source_path).name
                # figure.savefig(name.replace("wav", "png"))
                figure.savefig(buf, format="png")

                # # buffer = base64.b64encode(buf.getbuffer()).decode("ascii")
                buffer = pybase64.b64encode(buf.getbuffer()).decode("ascii")

                # print("Buffer len: ", len(buffer))

                return buffer

            except Exception as e:
                message = "SpectrogramCreator - Exception: " + e
                self.logger.debug(message)
                return None
        finally:
            self.is_running = False

    def setup_pitchshifting(
        self,
        sampling_freq_in,
        pitch_factor=10,
        volume_percent=50,  # 100,
        # overlap_factor=1.5,
        overlap_factor=2.5,
    ):
        """ """
        self.sampling_freq_in = int(sampling_freq_in)
        pitch_factor = int(pitch_factor)
        volume = int(volume_percent)
        self.pitch_div_factor = int(float(pitch_factor))
        self.volume = float((float(volume) / 100.0) * 1.0)
        self.overlap_factor = overlap_factor

        self.calc_pitchshifting_params()

    def calc_pitchshifting_params(self):
        """ """
        try:
            # Calculated parameters.
            self.time_exp_freq = int(self.sampling_freq_in / self.pitch_div_factor)
            self.hop_out_length = int(
                # self.sampling_freq_in / 1000 / self.pitch_div_factor
                self.sampling_freq_in
                / 1500
                / self.pitch_div_factor
            )
            self.hop_in_length = int(self.hop_out_length * self.pitch_div_factor)
            # Buffers.
            buffer_in_overlap_factor = float(self.overlap_factor)
            # kaiser_beta = int(self.pitch_div_factor * 0.8)
            kaiser_beta = 10
            self.window_size = int(self.hop_in_length * buffer_in_overlap_factor)
            self.window_function = numpy.kaiser(self.window_size, beta=kaiser_beta)

            # # For debug.
            # print("PitchShifting - freq_in: " + str(self.sampling_freq_in))
            # print("PitchShifting - volume: " + str(self.volume))
            # print("PitchShifting - pitch_factor: " + str(self.pitch_div_factor))
            # print("PitchShifting - time_exp_freq: " + str(self.time_exp_freq))
            # print("PitchShifting - hop_out_length: " + str(self.hop_out_length))
            # print("PitchShifting - hop_in_length: " + str(self.hop_in_length))
            # print("PitchShifting - kaiser_beta: " + str(kaiser_beta))
            # print("PitchShifting - window_size: " + str(self.window_size))

        except Exception as e:
            self.logger.error("SpectrogramCreator - calc_params: " + str(e))

    def calc_pitchshifting_mono(self, buffer_int16):
        """Pitch shifting of a single mono file.
        Simple time domain implementation by using overlapped
        windows and the Kaiser window function.
        """
        try:
            # Buffer delivered as int16. Transform to intervall -1 to 1.
            buffer_in = buffer_int16 / 32768.0

            pitchshifting_buffer_length = (
                len(buffer_in) / self.pitch_div_factor + self.window_size
            )  # + 1000
            buffer_out = numpy.zeros(
                int(pitchshifting_buffer_length), dtype=numpy.float32
            )

            # Check sound level. Reduce if necessary to avoid clipping.
            max_value = buffer_in.max() * self.volume + 0.20
            if max_value > 1.0:
                buffer_in = buffer_in / max_value
                # print("MAX VALUE: " + str(max_value - 0.20))

            # Add overlaps on pitchshifting_buffer. Window function is applied on "part".
            insert_pos = 0
            while buffer_in.size > self.window_size:
                part = buffer_in[: self.window_size] * self.window_function
                buffer_in = buffer_in[self.hop_in_length :]
                buffer_out[insert_pos : insert_pos + self.window_size] += part
                insert_pos += self.hop_out_length

            # Buffer to return. Convert to int16 and set volume.
            new_buffer_int16 = numpy.array(
                buffer_out[:insert_pos] * 32768.0 * self.volume, dtype=numpy.int16
            )

            # print("- Pitch buffer_in length: ", len(buffer_in))
            # print("- Pitch insert_pos: ", insert_pos)
            # print("- Pitch window_size: ", self.window_size)
            # print("- Pitch buffer_in max: ", buffer_int16.max())
            # print("- Pitch buffer_out max: ", new_buffer_int16.max())

            return new_buffer_int16

        except Exception as e:
            self.logger.debug(
                "SpectrogramCreator - Exception in calc_pithshifting_mono: " + str(e)
            )

        return None
