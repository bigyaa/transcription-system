# *************************************************************************************************************************
#   CONSTANTS.py 
#       Supporting program constants for audioDispatcher.py
# -------------------------------------------------------------------------------------------------------------------~~~~~~
#   Usage:
#      The module's identifiers define keys for values for config files, as well as file-related constants
# -------------------------------------------------------------------------------------------------------------------------
#   Design Notes:
#   -.  This module was tested using Python 3.12.  It hasn't been tested with earlier versions of Python.
#   -.  The e-mail regular expressions are potentially too restrictive. 
#       For more, see https://emaillistvalidation.com/blog/email-address-syntax/
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  1 April 2024
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
CONFIG_SCHEMA_KEY          = 'config_file_schema'
CONFIG_FILE_KEY            = 'config_file'
AUDIODIR_KEY               = "audiodir"
EXTENSIONS_KEY             = "extensions"
PYTHON_KEY                 = "/usr/bin/python3"
AUDIO_PROCESSOR_KEY        = "audio_processor"
PROCESSOR_CONFIG_FILE_KEY  = "processor_config_file"
ENABLE_LOGGING_KEY         = 'enable_logfile'
USER_LOGS_DIR_KEY          = 'user_logs_dir'
SUMMARY_LOG_NAME_KEY       = 'summary_log_name'
DETAILED_LOG_NAME_KEY      = 'detailed_log_name'
PERFORMANCE_LOG_NAME_KEY   = 'performance_log_name'
CONSOLE_DIR_KEY            = 'console_output_dir'
CONSOLE_NAME_KEY           = 'console_output_name'
CONSOLE_LEVEL_KEY          = 'console_severity_level'
CONSOLE_COLORIZE_KEY       = 'enable_console_colorize'
LOGFILE_DIR_KEY            = 'logfile_dir'
LOGFILE_NAME_KEY           = 'logfile_name'
LOGFILE_LEVEL_KEY          = 'logfile_severity_level'
LOGFILE_COLORIZE_KEY       = 'enable_logfile_colorize'
BATCH_SIZE_KEY             = "batch_size"
COMPUTE_TYPE_KEY           = "compute_type"
DEVICE_KEY                 = "device"
ENABLE_DIARIZATION_KEY     = "enable_diarization"
HF_TOKEN_KEY               = "hf_token"
MODEL_SIZE_KEY             = "model_size"
OUTPUT_DIR_KEY             = 'output_dir'
ENABLE_OVERWRITE_KEY       = "enable_overwrite"

# names for summary data performance parameters
#
TOTAL_RUN_TIME_KEY         = 'total_run_time'
MINUTES_KEY                = 'minutes'
SECONDS_KEY                = 'seconds'            
