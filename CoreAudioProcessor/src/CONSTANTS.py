# *************************************************************************************************************************
#   CONSTANTS.py 
#       Supporting program constants for coreAudioProcessor.py
# -------------------------------------------------------------------------------------------------------------------~~~~~~
#   Usage:
#      The module's identifiers define keys for values for config files, as well as file-related constants
# -------------------------------------------------------------------------------------------------------------------------
#   Design Notes:
#   -.  This module was tested using Python 3.12.  It hasn't been tested with earlier versions of Python.
#   -.  The e-mail regular expressions are potentially too restrictive. 
#       For more, see https://emaillistvalidation.com/blog/email-address-syntax/
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  15 May 2024
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
CONFIG_FILE_KEY          = 'config_processor'
CONFIG_SCHEMA_KEY        = 'config_file_schema'
INFILE_KEY               = 'recording'
BATCH_SIZE_KEY           = "batch_size"
COMPUTE_TYPE_KEY         = "compute_type"
DEVICE_KEY               = "device"
ENABLE_DIARIZATION_KEY   = "enable_diarization"
HF_TOKEN_KEY             = "hf_token"
MODEL_SIZE_KEY           = "model_size"
OUTPUT_DIR_KEY           = 'output_dir'
ENABLE_OVERWRITE_KEY     = "enable_overwrite"
ENABLE_LOGFILE_KEY       = 'enable_logfile'
PERFORMANCE_LOG_NAME_KEY = 'performance log'
CONSOLE_DIR_KEY          = 'console_output_dir'
CONSOLE_NAME_KEY         = 'console_output_name'
CONSOLE_LEVEL_KEY        = 'console_severity_level'
CONSOLE_COLORIZE_KEY     = 'enable_console_colorize'
LOGFILE_DIR_KEY          = 'logfile_dir'
LOGFILE_NAME_KEY         = 'logfile_name'
LOGFILE_LEVEL_KEY        = 'logfile_severity_level'
LOGFILE_COLORIZE_KEY     = 'enable_logfile_colorize'

# names for summary data performance parameters
#
INFILE_SIZE_KEY          = 'recording_size'
OUTPUT_FILE_KEY          = 'transcription'
STATUS_KEY               = 'status'
OUTCOME_KEY              = 'outcome'
TRANSCRIPTION_TIME_KEY   = 'transcription_time'
DIARIZATION_TIME_KEY     = 'diarization_time'
SPEAKER_TIME_KEY         = 'speaker_assignment_time'
TOTAL_TIME_KEY           = 'total_time'
MINUTES_KEY              = 'minutes'
SECONDS_KEY              = 'seconds'            
TOTAL_SEGMENT_COUNT_KEY  = 'total_segment_count'
BAD_SEGMENT_COUNT_KEY    = 'bad_segment_count'
BAD_SEGMENT_LIST_KEY     = 'bad_segment_list'

summary_data_keys  = [ STATUS_KEY, OUTCOME_KEY, TRANSCRIPTION_TIME_KEY, DIARIZATION_TIME_KEY ]
summary_data_keys += [ TRANSCRIPTION_TIME_KEY, DIARIZATION_TIME_KEY, SPEAKER_TIME_KEY, TOTAL_TIME_KEY ]
summary_data_keys += [ TOTAL_SEGMENT_COUNT_KEY, BAD_SEGMENT_COUNT_KEY, BAD_SEGMENT_LIST_KEY ]
null_transcription_data = lambda: dict( [ (key, None) for key in summary_data_keys ] )