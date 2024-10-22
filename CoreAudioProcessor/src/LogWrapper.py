# *************************************************************************************************************************
#   LogWrapper.py
#     A configurable wrapper for the Python logging module, supporting console and file logging with 
#     optional colorized output. It supports custom log formats and date formats.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The LogWrapper class is used to configure and initialize logging with predefined settings. It supports
#       customization of console and file log levels, output destinations, and whether to use color in output.
#
#       Parameters:
#           default_dict - A dictionary of default logging configurations including log levels, file paths, and colorization preferences.
#
#       Outputs:
#           Logging output to console and/or to a specified log file, with an optional colorized format for better readability.
#
#   Design Notes:
#   -.  LogRecordFormatter is a custom formatter class that extends logging.Formatter to add color support.
#   -.  LogWrapper sets up logging according to the configuration provided and applies the LogFormatter.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated: 18 March 2024
#   author: Phil Pfeiffer
#   adapted from code by Ruben Maharjan, Bigya Bajarcharya, and Mofeoluwa Jide-Jegede
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ---------------------------------------------------------------------------------------------------------------------
#   python standard library
# ---------------------------------------------------------------------------------------------------------------------
#
# logging - provides a flexible framework for emitting log messages from Python programs
#    logging.getLogger - return a logger with the specified name
#    logging.Formatter - class which formats logging records
#    logging.StreamHandler - sends logging output to streams like stdout or stderr
#    logging.FileHandler - sends logging output to a disk file
# os - provides a portable way of using operating system dependent functionality
#    devnull - alias for the null device
# pathlib - operating-system independent path construction
#    Path - generate a path from path segments
# sys - provides access to some variables used or maintained by the interpreter
#    sys.stdout, sys.stderr - file objects used by the print and exception calls to write their output
# threading - 
#    current_thread - identify current thread

import logging
import os
from pathlib import Path
import sys
import threading

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
# DEFAULTS - supporting definitions for forms parsing
#   LOG_RECORD_FORMAT_CONFIG - a dictionary containing the default settings for log record format and colorization
#
import src.DEFAULTS      as DEFAULT
import src.StatusManager as STATUS

# ***************************************************************************************************************************
# LogRecordFormatter:  Set up object for controlling the appearance of log records
#
#    Methods:
#     __init__():  set up parameters for formatting the log
#         Parameters:
#            useColor – determine whether to colorize log records
#       line_format():  return config module default for record format
#       date_format():  return config module default for date format
#       format(): format a log record
#         Parameters:
#           record – record to format
#         Outputs:
#           The formatted record
# ***************************************************************************************************************************

class LogRecordFormatter(logging.Formatter):

    @staticmethod
    def line_format(): return DEFAULT.LOG_RECORD_FORMAT_CONFIG['line_format']

    @staticmethod
    def date_format(): return DEFAULT.LOG_RECORD_FORMAT_CONFIG['date_format']

    def __init__(self, color, *args, **kwargs):
        super(LogRecordFormatter, self).__init__(*args, **kwargs)
        self.useColor = color
        self.colorCodes = DEFAULT.LOG_RECORD_FORMAT_CONFIG['color_codes']
        self.resetCode = DEFAULT.LOG_RECORD_FORMAT_CONFIG['reset']

    def format(self, record, *args, **kwargs):
        record.color_on, record.color_off = "", ""
        if (self.useColor and record.levelno in self.colorCodes):
            record.color_on = self.colorCodes[record.levelno]
            record.color_off = self.resetCode
        return super(LogRecordFormatter, self).format(record, *args, **kwargs)

# ***************************************************************************************************************************
# LogWrapper:  wrap the logging module, providing methods to set up logging
#
#    Methods:
#     __init__():  set up parameters for formatting the log
#         Parameters:
#            output_config: define the following parameters for logging operation -
#              console:
#                name– where to direct console messages
#                log_level – minimum level at which to log console messages
#                colorize – whether to colorize log console messages
#              logfile:
#                name – name of file
#                log_level – minimum level at which to log logfile messages
#                colorize – whether to colorize logfile  messages
#            record_config: define the following parameters for record formatting -
#               color_codes - colorization for critical, error, warning, info, and debug messages
#               reset - for resetting color codes
#               line_format - format for record lines
#               date_format - format for dates
#     set_up_logging(): 
#         initialize the logger, storing a reference ot the logger in ApplicationPreparserErrorManager.py's
#         information holder class
#     logger(): return the configured logger
# ***************************************************************************************************************************

class LogWrapper(object):

    def __init__(self, console_name, console_log_level, console_colorize, logfile_name, logfile_log_level, logfile_colorize, record_format=DEFAULT.LOG_RECORD_FORMAT_CONFIG):
        self.console_name =       console_name.lower()
        self.console_log_level =  console_log_level
        self.console_colorize =   console_colorize

        self.logfile_name =       logfile_name
        self.logfile_log_level =  logfile_log_level
        self.logfile_colorize =   logfile_colorize
        
        self.line_format = record_format['line_format']
        self.date_format = record_format['date_format']

    # Set up logging using the configuration values passed to the constructor
    def set_up_logging(self):

        # Create logger
        # For simplicity, we use the root logger, i.e. call 'logging.getLogger()' without a name argument.
        # This way we can use module methods for logging throughout the script.
        # An alternative would be exporting the logger, i.e.
        #     'global logger; logger = logging.getLogger("<name>")'
        self._logger = logging.getLogger()

        # Set global log level to 'debug' (required for handler levels to work)
        self._logger.setLevel(logging.DEBUG)

        # Create console handler, supporting shorthands
        if (self.console_name == "stdout"):
          self.console_name = sys.stdout
        elif (self.console_name == "stderr"):
          self.console_name = sys.stderr
        elif (self.console_log_output == "null"):
          self.console_name = os.devnull
        console_handler = logging.StreamHandler(self.console_name)

        # Set console log level
        try:
            # only accepts uppercase level names
            console_handler.setLevel(self.console_log_level.upper())
        except:
            print( STATUS.errmsg( f"LogWrapper: Failed to set console log level: invalid level ({self.console_log_level})", True ), file=sys.stderr)
            return False

        # Create and set formatter, add console handler to logger
        console_formatter = LogRecordFormatter( fmt=self.line_format, color=self.console_colorize, datefmt=self.date_format)
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)

        # Create log file handler, supporting shorthands
        if (self.logfile_name == "stdout"):
          logfile_handler = logging.FileHandler(sys.stdout)
        elif (self.logfile_name == "stderr"):
          logfile_handler = logging.FileHandler(sys.stderr)
        elif (self.logfile_name == "null"):
          logfile_handler = logging.FileHandler(os.devnull)
        else:
          logfile_dir = '.' if not len(Path(self.logfile_name).parents) else str(Path(self.logfile_name).parents[0])
          logfile_dir_absolute_path = Path( logfile_dir ).absolute()
          try:
            Path( logfile_dir_absolute_path ).mkdir(parents=True, exist_ok=True)
          except Exception as e:
            print( STATUS.errmsg( f"LogWrapper: Failed to create log file directory ({logfile_dir_absolute_path}): {STATUS.err_to_str(e)}", True ), file=sys.stderr)
            return False
          try:
            logfile_handler = logging.FileHandler(self.logfile_name)
          except Exception as e:
            print( STATUS.errmsg( f"LogWrapper: Failed to init log file ({self.logfile_name}): {STATUS.err_to_str(e)}", True ), file=sys.stderr)
            return False

        # Set log file log level
        try:
          # only accepts uppercase level names
          logfile_handler.setLevel(self.logfile_log_level.upper())
        except:
          print( STATUS.errmsg( f"LogWrapper: Failed to set log file log level: invalid level ({self.logfile_log_level})", True ), file=sys.stderr)
          return False

        # Create and set formatter, add log file handler to logger
        logfile_formatter = LogRecordFormatter(fmt=self.line_format, color=self.logfile_colorize, datefmt=self.date_format)
        logfile_handler.setFormatter(logfile_formatter)
        self._logger.addHandler(logfile_handler)

        # Success
        return True

    def logger(self):
      return logging.getLogger(threading.current_thread().name)
