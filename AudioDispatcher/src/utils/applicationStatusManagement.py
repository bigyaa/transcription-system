# *****************************************************************************************************************
#   applicationPreparserStatusManagement.py -
#       selected cross-module objects for error management
# -----------------------------------------------------------------------------------------------------------------
#   Usage:
#      This module's functions and classes in this module support the generation of program status messages.
# -------------------------------------------------------------------------------------------------------------------------
#   Design Notes:
#   -.  This module was tested using Python 3.12.  It hasn't been tested with earlier versions of Python.
#   -.  The module stands alone because of the need for cross-module management of program status messages,
#          particularly before applicationPreparser.py's logging has been enabled
# -----------------------------------------------------------------------------------------------------------------
#   last updated:  8 December 2023
#   author: Phil Pfeiffer
# *****************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ---------------------------------------------------------------------------------------
#   python standard library
# ---------------------------------------------------------------------------------------

# threading - 
#    current_thread - identify current thread
# time - 
#    ctime - returns current time of day

import threading
import time

my_generic_message = lambda message, show=False: f'{threading.current_thread().name}'+' '+time.ctime()+f"{': ' if show else ''}{message}"

def statusmsg( message, show_thread_and_time=False ):
  return my_generic_message( f'{statusmsg.filename} {message}', show_thread_and_time )
statusmsg.filename = ''

def errmsg( syndrome, show_thread_and_time=False ):
  return my_generic_message( f'?? {errmsg.filename} {syndrome}', show_thread_and_time )
errmsg.filename = ''

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# exception generation
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ConfigurationError(Exception): pass
class FileOpenError(Exception): pass
class FileTypeError(Exception): pass
class FileAccessError(Exception): pass
class FileFormatError(Exception): pass
class InternalError(Exception): pass

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# exit status management
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++++++++++++++++++
# Exit Status Codes
# +++++++++++++++++++++++++++++++++++++++++++++++

SUCCESS = 0
WARNING = 1
USAGE_ERROR = 2
ENVIRONMENT_ERROR = 3
INTERNAL_OPERATION_ERROR = 4

# ++++++++++++++++++++++++++++++++++++++++++++++++++
# ExitStatus
#
# singleton class for managing the exit status program wide. strategy:
# -.  init to SUCCESS
# -.  elevate to WARNING on nonfatal anomaly
# -.  elevate to ERROR on fatal anomaly
# ++++++++++++++++++++++++++++++++++++++++++++++++++

class ExitStatus(object):
  @staticmethod
  def application_format_irregularity():       
    ExitStatus.status = max(WARNING, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def missing_default_file():                  
    ExitStatus.status = max(WARNING, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def command_line_error():                    
    ExitStatus.status = max(USAGE_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def missing_file():                          
    ExitStatus.status = max(USAGE_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def file_type_error():                      
    ExitStatus.status = max(USAGE_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def file_format_error():                     
    ExitStatus.status = max(USAGE_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def file_access_error():                     
    ExitStatus.status = max(USAGE_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def improper_environmental_configuration():  
    ExitStatus.status = max(ENVIRONMENT_ERROR, ExitStatus.status)
    return ExitStatus.status
  @staticmethod
  def internal_error():  
    ExitStatus.status = max(INTERNAL_OPERATION_ERROR, ExitStatus.status)
    return ExitStatus.status

ExitStatus.status = SUCCESS
