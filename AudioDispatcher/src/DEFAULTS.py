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
#   last updated: 29 June 2024
#   authors: Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ===============================================
# Python library
# ===============================================
#
# datetime - module for manipulating dates and times
#    datetime.now - function to get the current date and time
# logging – access logging level definitions (CRITICAL, etc.)
# pathlib - operating-system independent path construction
#    Path - generate a path from path segments

from datetime import datetime
import logging
from pathlib import Path
import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# CONSTANTS - supporting definitions for program operation
#   shared designations for configurable parameters
#     CONFIG_SCHEMA_KEY         - XML file for validating configuration files
#     CONFIG_FILE_KEY           - XML file for overriding selected default values
#
#     PYTHON_KEY                - path to the Python interpreter
#     EXTENSIONS_KEY            - Extensions to treat as audio files in the specified directory tree
#     ENABLE_LOGGING_KEY        - whether to write to a log file
#     USER_LOGS_DIR_KEY         - target directory for user-visible logs
#     SUMMARY_LOG_NAME_KEY      - the name/ time/ status only log
#     DETAILED_LOG_NAME_KEY     - log for capturing all output from the audio processor
#     PERFORMANCE_LOG_NAME_KEY  - log for capturing all performance data from the audio processor
#
#     CONSOLE_DIR_KEY           - console output directory
#     CONSOLE_NAME_KEY          - console output name
#     CONSOLE_LEVEL_KEY         - severity level at which to log
#     CONSOLE_COLORIZE_KEY      - whether to colorize log messages
#     LOGFILE_DIR_KEY           - logfile directory
#     LOGFILE_NAME_KEY          - logfile name
#     LOGFILE_LEVEL_KEY         - severity level at which to log
#     LOGFILE_COLORIZE_KEY      - whether to colorize log messages
#
#     AUDIO_PROCESSOR_KEY       - path to the supporting single-file audio processor application
#     PROCESSOR_CONFIG_FILE_KEY - configuration file for the audio processor
#
#     BATCH_SIZE_KEY            - Number of audio segments to process simultaneously
#     COMPUTE_TYPE_KEY          - Type of computation (precision) to use, such as 'int8' or 'float16'
#     DEVICE_KEY                - Type of hardware device to use; either 'cpu' or 'gpu'
#     ENABLE_DIARIZATION_KEY    - specify whether to diarize as well as transcribe
#     HF_TOKEN_KEY              - Hugging Face (HF) authentication token for using models hosted on HF
#     MODEL_SIZE_KEY            - The Whisper model to use - 'tiny', 'base', 'small', 'medium', 'large'
#     OUTPUT_DIR_KEY            - directory for output from the program
#     ENABLE_OVERWRITE_KEY      - specify whether to overwrite transcription and diarization outputs, if present
 
import src.CONSTANTS  as CONST

# ==============================================================================================
# Non-logging output file system defaults
# ----------------------------------------------------------------------------------------------
#  Design notes:
#     Where 'None', the parameters will default to the parameters for the CoreAudioProcessor
# ==============================================================================================

# also in use by this project as a Hugging Face token: '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',

DISPATCHER_CONFIG = {
    CONST.CONFIG_SCHEMA_KEY:          str(Path( 'config', 'dispatcher_config_schema.xsd' )),
    CONST.CONFIG_FILE_KEY:            str(Path( 'config', 'dispatcher_config.xml' )),
    CONST.PYTHON_KEY:                 '/usr/bin/',
    CONST.EXTENSIONS_KEY:             ['.mp3', '.wav'],
    CONST.ENABLE_LOGGING_KEY:         True,
    CONST.USER_LOGS_DIR_KEY:          str(Path( 'logs' )),
    CONST.SUMMARY_LOG_NAME_KEY:       datetime.now().strftime('audioDispatcherSummary_%Y_%m_%d_%H_%M_%S.log'),
    CONST.DETAILED_LOG_NAME_KEY:      datetime.now().strftime('audioDispatcherDetailed_%Y_%m_%d_%H_%M_%S.log'),
    CONST.PERFORMANCE_LOG_NAME_KEY:   datetime.now().strftime('audioDispatcherPerformance_%Y_%m_%d_%H_%M_%S.log'),
    CONST.AUDIO_PROCESSOR_KEY:        str(Path( '..', 'CoreAudioProcessor', 'main.py' )),
    CONST.PROCESSOR_CONFIG_FILE_KEY:  None,
    CONST.BATCH_SIZE_KEY:             None,
    CONST.COMPUTE_TYPE_KEY:           None,
    CONST.DEVICE_KEY:                 None,
    CONST.ENABLE_DIARIZATION_KEY:     None,
    CONST.HF_TOKEN_KEY:               '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',
    CONST.MODEL_SIZE_KEY:             None,
    CONST.OUTPUT_DIR_KEY:             str(Path( 'transcriptions' )),
    CONST.ENABLE_OVERWRITE_KEY:       None,
}


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Log record format defaults
#     Log format:
#       color_codes – colorization for log records
#       reset – for absence of color
#       line_format – format for log entries
#       date_format – format for dating
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

LOG_RECORD_FORMAT_CONFIG = {
    'color_codes':  {
        logging.CRITICAL: '\033[1;35m', # bright/bold magenta
        logging.ERROR:    '\033[1;31m', # bright/bold red
        logging.WARNING:  '\033[1;33m', # bright/bold yellow
        logging.INFO:     '\033[0;37m', # white / light gray
        logging.DEBUG:    '\033[1;30m'  # bright/bold black / dark gray
    },
    'reset': '\033[0m',
    'line_format': \
         '%(color_on)s[%(asctime)s.%(msecs)03d] [%(threadName)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s%(color_off)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Logging output defaults
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

LOGGING_CONSOLE_CONFIG = {
    CONST.CONSOLE_DIR_KEY:       '',
    CONST.CONSOLE_NAME_KEY:      'stderr',
    CONST.CONSOLE_LEVEL_KEY:     'info',
    CONST.CONSOLE_COLORIZE_KEY:  True,
}

LOGFILE_CONFIG = {   
    CONST.LOGFILE_DIR_KEY:       'logs',
    CONST.LOGFILE_NAME_KEY:      datetime.now().strftime('audioDispatcherInternal_%H_%M_%d_%m_%Y.log'),
    CONST.LOGFILE_LEVEL_KEY:     'warning',
    CONST.LOGFILE_COLORIZE_KEY:  False,
}

NO_LOGFILE_CONFIG = {
    CONST.LOGFILE_DIR_KEY:       '',
    CONST.LOGFILE_NAME_KEY:      'null',
    CONST.LOGFILE_LEVEL_KEY:     'critical',
    CONST.LOGFILE_COLORIZE_KEY:  False,
}


