# *************************************************************************************************************************
#   DEFAULTS.py
#       Define default values and settings for an audio transcription system, including paths, file extensions, 
#       logging configurations, model types, and other constants for the system's default behavior.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       These constants should be imported and used by other modules, then overridden as required.
#
#   Design Notes:
#   -.  Default paths and filenames are provided for schema files, transcription directories, and log files.
#   -.  Default settings include file extensions for audio files, model types for transcription, and logging configurations.
#   -.  The datetime module is used to timestamp log files.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated: January 2024
#   authors: Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# datetime - module for manipulating dates and times
#    datetime.now - function to get the current date and time
# logging – access logging level definitions (CRITICAL, etc.)

from datetime import datetime
import logging

# ***********************************************
# Default values
# ***********************************************

DEFAULT_CONFIG_FILE = "./config/dev_config.xml"
DEFAULT_CONFIG_FILE_SCHEMA = './config/config_schema.xsd'
#
DEFAULT_AUDIO = './'  # Default audio directory if no other source is specified
DEFAULT_AUDIO_FILE_EXTENSIONS = ['.mp3', '.wav', '.aac']
DEFAULT_XML_PATH = "./config/dev_config.xml"

# ===============================================
#  Log record format defaults
#     Log format:
#       color_codes – colorization for log records
#       reset – for absence of color
#       line_format – format for log entries
#       date_format – format for dating
# ===============================================

DEFAULT_LOG_RECORD_FORMAT_CONFIG = {
    'color_codes':  {
        logging.CRITICAL: "\033[1;35m", # bright/bold magenta
        logging.ERROR:    "\033[1;31m", # bright/bold red
        logging.WARNING:  "\033[1;33m", # bright/bold yellow
        logging.INFO:     "\033[0;37m", # white / light gray
        logging.DEBUG:    "\033[1;30m"  # bright/bold black / dark gray
    },
    'reset': "\033[0m",
    'line_format': \
         "%(color_on)s[%(asctime)s.%(msecs)03d] [%(threadName)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s%(color_off)s",
    'date_format': "%Y-%m-%d %H:%M:%S"
}
# ===============================================
#  Logging defaults
#     console:
#       output – where to direct console messages
#       log_level – minimum level at which to log console messages
#       colorize – whether to colorize log console messages
#     logfile:
#       path – path to file (ignored if name set to stdout or stderr)
#       name – name of file
#       log_level – minimum level at which to log logfile messages
#       colorize – whether to colorize logfile  messages
# ===============================================

DEFAULT_LOGGING_CONFIG = {
    'console': {
        'output': 'stderr',
        'log_level': "info",
        'colorize': True
    },
    'logfile': {
        'path': "logs",
        'name': datetime.now().strftime('ISC_%H_%M_%d_%m_%Y.log'),
        'log_level': "debug",
        'colorize': False
    }
}


# ===============================================
#  Whisper defaults
#     batch_size – Number of audio segments to process simultaneously
#     compute_type – Type of computation (precision) to use, such as 'int8' or 'float16'
#     device – Type of hardware device to use; either 'cpu' or 'gpu'
#     diarize – specify whether to diarize as well as transcribe
#     hf_token – Hugging Face authentication token for using models hosted on Hugging Face
#     model_size – The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large')
#     audiodir – The directory that contains audio files
#     output_dir – The directory where the transcriptions will be written
# ===============================================

ALLOWED_MODEL_TYPES = ['tiny', 'base', 'small', 'medium', 'large']
DEFAULT_WHISPER_CONFIG = {
    'batch_size': 1,
    'compute_type': 'int8',
    'device':  'cpu',
    'diarize':  False,
    'hf_token': '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',
    'model_size': 'small',
    'audiodir': './',
    'output_dir': './transcriptions/',
}
