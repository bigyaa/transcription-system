# *************************************************************************************************************************
#   CommandLineParser.py
#       Provide command-line parsing for the WhisperX-driven batch processing transcription and diarization application.
# -----------------------------------------------------------------------------------------------------------------------
#   Usage:
#       Call parse_command_line_args() to parse and retrieve command-line arguments.
#
#       Parameters:
#           Command-line parameters are supported for specifying audio files, configuration XML, model type,
#           directories for audio files and transcriptions, user tokens for diarization, allowed file extensions,
#           and logging options.
#
#       Outputs:
#           Command-line parsing results in a namespace of parsed arguments.
#
#   Design Notes:
#   -.  The module is designed to be used as a utility in a larger audio transcription application.
#   -.  Logging is configured to provide info and critical feedback for the operations performed.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  17 May 2024
#   authors:  Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ---------------------------------------------------------------------------------------
#   python standard library
# ---------------------------------------------------------------------------------------
#
# argparse - command-line parsing library
#    ArgumentParser - class to parse command-line options
# pathlib - path processing
#    Path - class for path manipulation
# sys –
#    exit – exit, returning a final status code
#    stderr – the standard error message stream

import argparse
from pathlib import Path
import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# StatusManager - supporting definitions for error management
# CONSTANTS - supporting definitions for program operation
#   shared designations for configurable parameters
#     CONFIG_FILE_KEY           - XML file for overriding selected default values
#     AUDIODIR_KEY              - directory containing input to transcribe
#     EXTENSIONS_KEY            - Extensions to treat as audio files in the specified directory tree
#     PYTHON_KEY                - path to the Python interpreter
#     ENABLE_LOGFILE_KEY        - whether to write to a log file
#     USER_LOGS_DIR_KEY         - target directory for user-visible logs
#     SUMMARY_LOG_NAME_KEY      - 'summary_log_name'
#     DETAILED_LOG_NAME_KEY     - 'detailed_log_name'
#     PERFORMANCE_LOG_NAME_KEY  - log for capturing all performance data from the audio processor
#
#     AUDIO_PROCESSOR_KEY       - path to the supporting single-file audio processor application
#     PROCESSOR_CONFIG_FILE_KEY - configuration file for the audio processor
#     BATCH_SIZE_KEY            - Number of audio segments to process simultaneously
#     COMPUTE_TYPE_KEY          - Type of computation (precision) to use, such as 'int8' or 'float16'
#     DEVICE_KEY                - Type of hardware device to use; either 'cpu' or 'gpu'
#     ENABLE_DIARIZATION_KEY    - specify whether to diarize as well as transcribe
#     HF_TOKEN_KEY              - Hugging Face (HF) authentication token for using models hosted on HF
#     MODEL_SIZE_KEY            - The Whisper model to use - 'tiny', 'base', 'small', 'medium', 'large'
#     OUTPUT_DIR_KEY            - directory for output from the program
#     ENABLE_OVERWRITE_KEY      - specify whether to overwrite transcription and diarization outputs, if present

import src.StatusManager as STATUS
import src.CONSTANTS     as CONST

# ***********************************************
#  helper functions proper
# ***********************************************

def str2bool(v):
    """
    Convert a string to one of True, False

    Args:
        v (str): The input string.
    Returns:
        The corresponding boolean value, or "none" if it's neither.
        None implies a need to check config files or defaults for a key's value.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    return False

# parse a directory name, verifying the directory's existence
#
class directory_parser(argparse.Action):
  """ parse a directory path """
  #
  def __init__(self, option_strings, dest, nargs=None, **kwargs):
    super(directory_parser, self).__init__(option_strings, dest, **kwargs)
  #
  def __call__(self, parser, namespace, dirname, option_string=None):
    if dirname is None:
      raise argparse.ArgumentTypeError( f'\ninvalid directory name option: name must be present' )
    if dirname == '':
      raise argparse.ArgumentTypeError( f'\ninvalid directory name option: name must be nonempty' )
    # the following call fails when invoked with just "dirname" - perhaps an issue ih the Windows library?
    if not Path( dirname ).exists():
      raise argparse.ArgumentTypeError( f'\nspecified directory ({dirname}) not found' )
    if not Path( dirname ).is_dir():
      raise argparse.ArgumentTypeError( f'\nspecified name ({dirname}) must be a directory' )
    setattr(namespace, self.dest, dirname )

def parse_command_line_args():
    """
    Parse command line arguments and return the parsed arguments.

    Returns:
        dict: Parsed command line arguments as a dictionary.
    """
    parser = argparse.ArgumentParser( description="Process command-line arguments for audio transcription." )
    #
    parser.add_argument("-cxds", "--config_dispatcher",   help="An alternative xml config file for this application", dest=CONST.CONFIG_FILE_KEY)
    parser.add_argument("-au",   "--audiodir",            action=directory_parser, help="The directory tree with the audio files to process", dest=CONST.AUDIODIR_KEY, required=True) 
    parser.add_argument('-ex',   '--extensions',          help="List of file extensions to treat as recordings", dest=CONST.EXTENSIONS_KEY )
    #
    parser.add_argument("-py",   "--python",                   help="Path to the python interpreter", dest=CONST.PYTHON_KEY)
    parser.add_argument("-pr",   "--audio_processor",          help="Path to the single-file audio processor app", dest=CONST.AUDIO_PROCESSOR_KEY)
    parser.add_argument('-el',   '--enable_logfile',           help="If true, enable logfile output", dest=CONST.ENABLE_LOGGING_KEY, type=str2bool, default=True, nargs='?' )
    parser.add_argument("-ld",   "--logfile_dir",              help="Directory for user-visible log files", dest=CONST.USER_LOGS_DIR_KEY)
    parser.add_argument("-lnsm", "--summary_logfile_name",     help="Summary log file name", dest=CONST.SUMMARY_LOG_NAME_KEY)
    parser.add_argument("-lndt", "--detailed_logfile_name",    help="Detailed log file name", dest=CONST.DETAILED_LOG_NAME_KEY)
    parser.add_argument("-lnpf", "--performance_logfile_name", help="Performance data log file name", dest=CONST.PERFORMANCE_LOG_NAME_KEY)
    #
    parser.add_argument("-cxpr", "--config_processor",    help="An alternative xml config file for the audio processor",  dest=CONST.PROCESSOR_CONFIG_FILE_KEY)
    #
    parser.add_argument("-bs",   "--batch_size",          help="The batch size for transcription", dest=CONST.BATCH_SIZE_KEY)
    parser.add_argument("-ct",   "--compute_type",        help="Specifies the computation type", dest=CONST.COMPUTE_TYPE_KEY)
    parser.add_argument("-dv",   "--device",              help="Hardware device for diarization", dest=CONST.DEVICE_KEY)
    parser.add_argument("-ed",   "--enable_diarization",  help="If true, diarize after transcription", dest=CONST.ENABLE_DIARIZATION_KEY, type=str2bool, default=True, nargs='?' )
    parser.add_argument("-ht",   "--hf_token",            help="The user token needed for diarization", dest=CONST.HF_TOKEN_KEY)
    parser.add_argument("-ms",   "--model_size",          help="The model size for transcription", dest=CONST.MODEL_SIZE_KEY)
    parser.add_argument("-od",   "--output_dir",          help="The directory to store transcriptions", dest=CONST.OUTPUT_DIR_KEY)
    parser.add_argument('-ov',   '--overwrite',           help="If true, overwrite existing output", dest=CONST.ENABLE_OVERWRITE_KEY, type=str2bool, default=True, nargs='?' )
    
    try:
        return vars(parser.parse_args())
    except Exception as e:
        print( STATUS.errmsg( "\nparse_command_line_args: " + STATUS.err_to_str(e) + ' - exiting ', True ), file=sys.stderr )
        sys.exit(STATUS.ExitStatus.command_line_error())
