# *************************************************************************************************************************
#   ISCLogWrapper.py
#       This module defines a wrapper for the Python logging module, providing a convenient setup for console and
#       file logging with optional colorized output. It is configurable via a dictionary of default values and supports
#       custom log formats and date formats.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The ISCLogWrapper class is used to configure and initialize logging with predefined settings. It supports
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
#   -.  ISCLogWrapper sets up logging according to the configuration provided and applies the LogFormatter.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated: 3 March 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
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
#    os.path.join - join one or more path components intelligently
# sys - provides access to some variables used or maintained by the interpreter
#    sys.stdout, sys.stderr - file objects used by the print and exception calls to write their output
# threading - 
#    current_thread - identify current thread

import logging
import os
import sys
import threading

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# DEFAULTS - supporting definitions for forms parsing
#   LOG_RECORD_FORMAT_CONFIG - a dictionary containing the default log record configuration settings
# StatusManager - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
#
import src.DEFAULTS as DEFAULT
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
# ISCLogWrapper:  wrap the logging module, providing methods to set up logging
#
#    Methods:
#     __init__():  set up parameters for formatting the log
#         Parameters:
#            log_dict: define the following parameters for logging operation –
#                console_log_output– where to direct console messages
#                console_log_level – minimum level at which to log console messages
#                console_colorize – whether to colorize log console messages
#                logfile_dir– path to file (ignored if name set to stdout or stderr)
#                logfile_name – name of file
#                logfile_log_level – minimum level at which to log logfile messages
#                logfile_colorize – whether to colorize logfile  messages
#     logger(): return the configured logger
# ***************************************************************************************************************************

class ISCLogWrapper(object):

    def __init__(self, console_config, logfile_config, record_format):
        self.console_log_output = console_config['output']
        self.console_log_level =  console_config['log_level']
        self.console_colorize =   console_config['colorize']

        self.logfile_dir =        logfile_config['dir']
        self.logfile_name =       logfile_config['name']
        self.logfile_log_level =  logfile_config['log_level']
        self.logfile_colorize =   logfile_config['colorize']
        
        self.line_format = record_format['line_format']
        self.date_format = record_format['date_format']

    # Set up logging using the configuration values passed to the constructor
    # For simplicity, we use the root logger, i.e. call 'logging.getLogger()' without a name argument.
    # This way we can use module methods for logging throughout the script.
    # An alternative would be exporting the logger, i.e.
    #     'global logger; logger = logging.getLogger("<name>")'
    #
    def set_up_logging(self):

        # Create logger
        self._logger = logging.getLogger()

        # Set global log level to 'debug' (required for handler levels to work)
        self._logger.setLevel(logging.DEBUG)

        # Create console handler
        console_log_output = self.console_log_output.lower()
        if (self.console_log_output == "stdout"):
            console_log_output = sys.stdout
        elif (self.console_log_output == "stderr"):
            console_log_output = sys.stderr
        elif (self.console_log_output == "os.devnull"):
            console_log_output = os.devnull
        else:
            print( STATUS.errmsg( f"LogWrapper: Failed to set console output: invalid output ({self.console_log_output})", True ), file=sys.stderr)
            return False
        console_handler = logging.StreamHandler(console_log_output)

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

        # Create log file handler
        try:
            if (console_log_output == "stdout"):
                logfile_name = 'the standard output'
                logfile_handler = logging.FileHandler(sys.stdout)
            elif (console_log_output == "stderr"):
                logfile_name = 'the standard error'
                logfile_handler = logging.FileHandler(sys.stderr)
            elif (console_log_output == "os.devnull"):
                logfile_name = 'the null device'
                logfile_handler = logging.FileHandler(os.devnull)
            else:
                logfile_name = os.path.join(self.logfile_dir, self.logfile_name)
                if not os.path.exists( os.path.abspath( self.logfile_dir ) ): 
                    try:
                        os.makedirs( os.path.abspath( self.logfile_dir ) )
                    except Exception as e:
                        print( STATUS.errmsg( f"LogWrapper: Failed to init log file ({logfile_name}): {STATUS.err_to_str(e)}", True ), file=sys.stderr)
                        return False
                logfile_handler = logging.FileHandler(logfile_name)
        except Exception as e:
            print( STATUS.errmsg( f"LogWrapper: Failed to init log file ({logfile_name}): {STATUS.err_to_str(e)}", True ), file=sys.stderr)
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
