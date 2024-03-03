# *************************************************************************************************************************
#   TranscriptionConfig.py
#       Manage the configuration for an audio transcription system, including access to XML configuration files.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The module provides an interface for interacting with the transcription configuration through the
#       TranscriptionConfig class. Functions are also available for parsing command-line arguments and for
#       validating XML configuration files.
#
#       Parameters:
#           Various parameters can be defined in an XML configuration file, which are then parsed and applied to
#           the transcription system. Command-line arguments can override configuration file settings.
#
#       Outputs:
#           The TranscriptionConfig class provides methods to retrieve and set configuration values, and to
#           create or delete configuration keys.
#
#   Design Notes:
#   -.  The module uses lxml for XML parsing and validation.
#   -.  Custom utility functions are used for command-line parsing and XML validation.
#   -.  The logging module provides feedback and error reporting.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  1 March 2024
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
# sys –
#   exit – exit, returning a final status code
#   stderr – the standard error message stream

import copy
import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# CommandLineParser - supporting functions for parsing the command line
#   parse_command_line_args - parse the command line arguments, returning a dict
# DEFAULTS - supporting definitions for forms parsing
#   LOGFILE_CONFIG, NO_LOGFILE_CONFIG, LOGGING_CONSOLE_CONFIG - logging output params
#   LOG_RECORD_FORMAT_CONFIG - logging record output format params
#   WHISPER_CONFIG - user-configurable parameters
# ISCLogWrapper - supports logging
#   ISCLogWrapper - initializes logging
# StatusManager - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
# XMLProcessor - manipulate XML files and content
#   XMLFile - parse and validate XML files

import src.CommandLineParser as CL_PARSE
import config.DEFAULTS as DEFAULT
import src.ISCLogWrapper as LOGGER
import src.StatusManager as STATUS
import src.XMLProcessor as XML

# ***********************************************
#  main module
# ***********************************************

# =======================================================================================================
# read XML configuration files for the transcription system.
# =======================================================================================================

class TranscriptionConfig():
    def __init__(self, audio=None):
      # *** *** parse the command line *** ****  
      self.command_line_args = copy.deepcopy( CL_PARSE.parse_command_line_args() )
      
      # *** *** set up file name for informational and error messages *** ***
      self.audio_file = audio if audio else self.command_line_args['audio_file']
      STATUS.statusmsg.filename = self.audio_file
      STATUS.errmsg.filename = self.audio_file
      
      # *** *** locate and attempt to parse the config file - user-specified (priority) or default ***
      #
      config_file = ( self.command_line_args['configxml'], ) if self.command_line_args['configxml'] else ()
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
      enable_logfile =\
        eval(self.command_line_args['enable_logfile']) if self.command_line_args['enable_logfile'] else \
        ( self.config_file_data['enable_logfile'] if ('enable_logfile' in self.config_file_data) \
          else DEFAULT.WHISPER_CONFIG['enable_logfile'] )
  
      if enable_logfile:
          logfile_config = copy.deepcopy(DEFAULT.LOGFILE_CONFIG)
             
          if self.command_line_args['logfile']:
              logfile_config['name'] = self.command_line_args['logfile']
          elif 'logfile' in self.config_file_data:
              logfile_config['name'] = self.config_file_data['logfile']
      else:
          logfile_config = copy.deepcopy(DEFAULT.NO_LOGFILE_CONFIG)
  
      console_config = copy.deepcopy(DEFAULT.LOGGING_CONSOLE_CONFIG)
      log_record_format_config = copy.deepcopy(DEFAULT.LOG_RECORD_FORMAT_CONFIG)

      log_wrapper = LOGGER.ISCLogWrapper(console_config, logfile_config, log_record_format_config)
      if not log_wrapper.set_up_logging():
          print( STATUS.errmsg( 'ConfigManager: could not set up logging', True ), file=sys.stderr )
          sys.exit(STATUS.ExitStatus.improper_environmental_configuration())

      self._logger = log_wrapper.logger()

    def get(self, key):
        """
        Get the value for the specified key in the configuration file.
        """
        try:
            if key in self.command_line_args and self.command_line_args[key] is not None:
                return self.command_line_args[key]
            elif key in self.config_file_data:
                return self.config_file_data[key]
            elif key in DEFAULT.WHISPER_CONFIG:
                return DEFAULT.WHISPER_CONFIG[key]
            self._logger.error( f'Could not find element in configuration file: {key}')
            sys.exit(STATUS.ExitStatus.internal_error())
        except Exception as e:
            self._logger.error( f'Error accessing configuration file: {STATUS.err_to_str(e)}')
            sys.exit(STATUS.ExitStatus.internal_error())

    def logger(self):
      return self._logger
