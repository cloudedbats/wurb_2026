#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Cloudedbats WURB-2026.

import os
import sys
import pathlib

__version__ = "2026.0.0-development"

# Absolute paths to working directory and executable.
workdir_path = pathlib.Path(__file__).parent.parent.resolve()
executable_path = pathlib.Path(os.path.dirname(sys.argv[0]))
print()
print("DEBUG: Working directory path: ", str(workdir_path))
print("DEBUG: Executable path: ", str(executable_path))

logger_name = "WurbLogger"
logging_dir = pathlib.Path(executable_path.parent, "wurb_logging")
log_file_name = "wurb_info_log.txt"
debug_log_file_name = "wurb_debug_log.txt"
settings_dir = pathlib.Path(executable_path.parent, "wurb_settings")
config_dir = pathlib.Path(executable_path.parent, "wurb_settings")
config_file = "wurb_config.yaml"
config_default_file = pathlib.Path(workdir_path, "wurb_config_default.yaml")

# import pyaudio
import wurb_utils

from wurb_core.common.wurb_logger import WurbLogger
from wurb_core.common.wurb_settings import WurbSettings
from wurb_core.common.wurb_manager import WurbManager

from wurb_core.record.rec_manager import RecManager
from wurb_core.record.rec_devices import RecDevices
from wurb_core.record.rec_worker import RecWorker
from wurb_core.record.rec_sound_detection import SoundDetection
from wurb_core.record.rec_scheduler import WurbScheduler
from wurb_core.record.rec_status import RecStatus
from wurb_core.record.rpi_control import WurbRaspberryPi
from wurb_core.record.gps_reader import GpsReader
from wurb_core.record.rec_file_writer import RecFileWriter

from wurb_core.administration.sources_and_files import SourcesAndFiles
from wurb_core.annotations.metadata import Metadata
from wurb_core.annotations.record_manager import RecordManager
from wurb_core.annotations.spectrogram import SpectrogramCreator

from wurb_core.administration.admin_manager import AdminManager
from wurb_core.administration.cleanup import AdminCleanup
from wurb_core.administration.report_excel import ReportExcel


# Instances of objects.

# Configuration and logging.
config = wurb_utils.Configuration(logger_name=logger_name)
config.load_config(
    config_dir=config_dir,
    config_file=config_file,
    config_default_file=config_default_file,
)
logger = wurb_utils.Logger(logger_name=logger_name)

# Basic WURB.
wurb_logger = WurbLogger(config, logger_name=logger_name)
wurb_settings = WurbSettings(config, wurb_logger)
wurb_manager = WurbManager(config, wurb_logger)

# Audio.
sound_pitch_shifting = wurb_utils.SoundPitchShifting(logger_name=logger_name)
# audio = pyaudio.PyAudio()  # Only one instance allowed.
# audio_capture = wurb_utils.AudioCapture(audio, logger_name=logger_name)
# audio_playback = wurb_utils.AudioPlayback(audio, logger_name=logger_name)
audio_capture = wurb_utils.AudioCapture(logger_name=logger_name)
# Pettersson M500.
m500 = wurb_utils.PetterssonM500(logger_name=logger_name)

# Record.
rec_manager = RecManager(config, wurb_logger)
rec_devices = RecDevices(config, wurb_logger)
rec_worker = RecWorker(config, wurb_logger)
sound_detection = SoundDetection(logger_name=logger_name)
rec_scheduler = WurbScheduler(config, wurb_logger)
rec_status = RecStatus(config, wurb_logger)
wurb_rpi = WurbRaspberryPi(config, wurb_logger)
gps_reader = GpsReader(config, wurb_logger)

# Annotations and administration.
sources_and_files = SourcesAndFiles(config, wurb_logger)
metadata = Metadata(config, logger)
record_manager = RecordManager(config, wurb_logger)
spectrogram = SpectrogramCreator(config, wurb_logger)

# Administration.
admin_manager = AdminManager(config, wurb_logger)
cleanup = AdminCleanup(config, wurb_logger)
report_excel = ReportExcel(config, wurb_logger)

# Sunset, sunrise, etc.
sun_moon = wurb_utils.SunMoon()
