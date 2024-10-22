# *************************************************************************************************************************
#   TranscriptionConfig.py
#       Manage the configuration for an audio transcription system, including access to XML configuration files.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The module provides an interface for interacting with the transcription configuration through the
#       TranscriptionConfig class.  This class provides methods to initialize and retrieve this application's
#       configuration values.
#   Operation:
#       Parameters for the program's operation are retrieved from the following hierarchy of data sources,
#       with precedence as shown below:
#       -.  command line options
#       -.  user-specified configuration file (specified on the command line)
#       -.  default configuration file
#       -.  program DEFAULTS module
#       Supporting routines are provided for retrieving these parameters, once initialized.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  17 May 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# --------------------------------------------------------------------------------------
#   Python Standard Library
# --------------------------------------------------------------------------------------
#
# copy –
#   deepcopy - copy the entirety of the specified argument
# pathlib - operating-system independent path construction
#    Path - generate a path from path segments
# sys –
#   exit – exit, returning a final status code
#   stderr – the standard error message stream

import copy
from pathlib import Path
import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# StatusManager - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
# CONSTANTS - supporting definitions for program operation
#   shared designations for configurable parameters
#     CONFIG_FILE_KEY        - XML file for overriding selected default values
#     AUDIODIR_KEY           - directory containing input to transcribe
#     ENABLE_LOGFILE_KEY     - whether to write to a log file
#     USER_LOGS_DIR_KEY      - target directory for user-visible logs
#     SUMMARY_LOG_NAME_KEY   - the name/ time/ status only log
#     DETAILED_LOG_NAME_KEY  - log for capturing all output from the audio processor
#     PERFORMANCE_LOG_NAME_KEY  - log for capturing all performance data from the audio processor
#
#     CONSOLE_DIR_KEY        - console output directory
#     CONSOLE_NAME_KEY       - console output name
#     CONSOLE_LEVEL_KEY      - severity level at which to log
#     CONSOLE_COLORIZE_KEY   - whether to colorize log messages
#     LOGFILE_NAME_KEY       - default internal logfile name
#     LOGFILE_LEVEL_KEY      - severity level at which to log
#     LOGFILE_COLORIZE_KEY   - whether to colorize log messages
# DEFAULTS - supporting definitions for forms parsing
#   DISPATCHER_CONFIG - user-configurable parameters
# ISCLogWrapper - supports logging
#   ISCLogWrapper - initializes logging
# XMLProcessor - manipulate XML files and content
#   XMLFile - parse and validate XML files
# CommandLineParser - supporting functions for parsing the command line
#   parse_command_line_args - parse the command line arguments, returning a dict

import src.CONSTANTS         as CONST
import src.DEFAULTS          as DEFAULT
import src.LogWrapper        as LOGGER
import src.StatusManager     as STATUS
import src.XMLProcessor      as XML
import src.CommandLineParser as CL

# ***********************************************
#  main module
# ***********************************************

# =======================================================================================================
# initialize (__init__) and provide access to segment merger operating parameters
# =======================================================================================================

class TranscriptionConfig():
  def __init__(self):
    self._logger      = None

    # *** *** parse the command line *** ****  
    self.command_line_args = copy.deepcopy( CL.parse_command_line_args() )
    
    # *** *** set up file name for informational and error messages *** ***
    self._application_file    = self.command_line_args[CONST.AUDIODIR_KEY]
    STATUS.statusmsg.filename = self._application_file
    STATUS.errmsg.filename    = self._application_file
    
    # *** *** locate and attempt to parse the config file - user-specified (priority) or default ***
    #
    config_file = () if self.command_line_args[CONST.CONFIG_FILE_KEY] is None else (self.command_line_args[CONST.CONFIG_FILE_KEY], )
    parsed_config_file = XML.XMLFile( *config_file ) 
    ( self.config_file_data, file_missing, file_malformed, schema_missing, schema_malformed, file_invalid ) = parsed_config_file.contents()
    
    fatal_errors = '\n'.join( (file_missing if config_file else []) + file_malformed + schema_malformed + file_invalid  )
    if fatal_errors:
      print( STATUS.errmsg( "ConfigManager: " + fatal_errors, True ), file=sys.stderr )
      sys.exit(STATUS.ExitStatus.missing_file())
      
    warnings = '\n'.join( file_missing + schema_missing )
    if warnings:  
      print( STATUS.statusmsg( warnings ), file=sys.stderr )
      STATUS.ExitStatus.missing_default_file()
   
    # *** configure logging ***
    #
    config_dict       = DEFAULT.LOGGING_CONSOLE_CONFIG
    console_name      = str(Path(self.get(CONST.CONSOLE_DIR_KEY,  config_dict), self.get(CONST.CONSOLE_NAME_KEY, config_dict)))
    console_log_level = self.get(CONST.CONSOLE_LEVEL_KEY,    config_dict)
    console_colorize  = self.get(CONST.CONSOLE_COLORIZE_KEY, config_dict)

    config_dict       = DEFAULT.DISPATCHER_CONFIG if self.get(CONST.ENABLE_LOGGING_KEY) else DEFAULT.NO_LOGFILE_CONFIG
    logfile_dir       = str(Path(self.get(CONST.USER_LOGS_DIR_KEY, config_dict)))
    
    config_dict       = DEFAULT.LOGFILE_CONFIG if self.get(CONST.ENABLE_LOGGING_KEY) else DEFAULT.NO_LOGFILE_CONFIG
    logfile_name      = config_dict[CONST.LOGFILE_NAME_KEY]
    logfile_log_level = self.get(CONST.LOGFILE_LEVEL_KEY,    config_dict)
    logfile_colorize  = self.get(CONST.LOGFILE_COLORIZE_KEY, config_dict)

    log_params = ( console_name, console_log_level, console_colorize, logfile_dir, logfile_name, logfile_log_level, logfile_colorize )
    log_wrapper = LOGGER.LogWrapper( *log_params )
    if not log_wrapper.set_up_logging():
      print( STATUS.errmsg( 'ConfigManager: could not set up logging', True ), file=sys.stderr )
      sys.exit(STATUS.ExitStatus.improper_environmental_configuration())
    self._logger = log_wrapper.logger()

  def get(self, key, config_dict=DEFAULT.DISPATCHER_CONFIG):
    """
    Get the value for the specified key in the configuration file.
    """
    if key in self.command_line_args and self.command_line_args[key] is not None:
      return self.command_line_args[key]
    elif key in self.config_file_data:
      if key.startswith('enable_'):
        return CL.str2bool(self.config_file_data[key])
      else:
        return self.config_file_data[key]
    elif key in config_dict:
      return config_dict[key]
    err_msg = f' Error accessing configuration parameter: cannot access {key} key'
    if self._logger:
      self._logger.error( STATUS.errmsg( err_msg ) )
    else:
      print( STATUS.errmsg( err_msg, True ), file=sys.stderr )   
    sys.exit(STATUS.ExitStatus.internal_error())

  def logger(self):     return self._logger
