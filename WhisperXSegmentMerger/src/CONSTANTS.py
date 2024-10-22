# *************************************************************************************************************************
#   CONSTANTS.py 
#       Supporting program constants for WhisperXSegmentMerger.py
# -------------------------------------------------------------------------------------------------------------------~~~~~~
#   Usage:
#      The module's identifiers define keys for values for config files, as well as file-related constants
# -------------------------------------------------------------------------------------------------------------------------
#   Design Notes:
#   -.  This module was tested using Python 3.12.  It hasn't been tested with earlier versions of Python.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  17 May 2024
#   author:        Phil Pfeiffer
# *************************************************************************************************************************

# *************************************************************************************************************************
# Tags for keys for configurable parameters that are shared between modules
#
# Design note:
# -. keys must be identical to names used in configuration files.
#    currently, no logic checks for consistency with element names in the configuration file schema
# *************************************************************************************************************************

# names for config-file and command-line common configurable parameters
#
INFILE_KEY               = 'transcript'
CONFIG_FILE_KEY          = 'config_processor'
CONFIG_SCHEMA_KEY        = 'config_file_schema'
OUTPUT_DIR_KEY           = 'output_dir'
OUTPUT_FILE_KEY          = 'updated_transcript'
ENABLE_LOGFILE_KEY       = 'enable_logfile'
CONSOLE_DIR_KEY          = 'console_output_dir'
CONSOLE_NAME_KEY         = 'console_output_name'
CONSOLE_LEVEL_KEY        = 'console_severity_level'
CONSOLE_COLORIZE_KEY     = 'enable_console_colorize'
LOGFILE_DIR_KEY          = 'logfile_dir'
LOGFILE_NAME_KEY         = 'logfile_name'
LOGFILE_LEVEL_KEY        = 'logfile_severity_level'
LOGFILE_COLORIZE_KEY     = 'enable_logfile_colorize'
