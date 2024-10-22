# *************************************************************************************************************************
#   CommandLineParser.py
#       Provide command-line parsing for the WhisperX-driven transcription and diarization application.
# -------------------------------------------------------------------------------------------------------------------
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
# sys –
#   exit – exit, returning a final status code
#   stderr – the standard error message stream

import argparse
import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# StatusManager - supporting definitions for error management
# CONSTANTS - supporting definitions for program operation
#   shared designations for configurable parameters
#     CONFIG_FILE_KEY           - XML file for overriding selected default values
#     INFILE_KEY                - input to transcribe
#     BATCH_SIZE_KEY            - Number of audio segments to process simultaneously
#     COMPUTE_TYPE_KEY          - Type of computation (precision) to use, such as 'int8' or 'float16'
#     DEVICE_KEY                - Type of hardware device to use; either 'cpu' or 'gpu'
#     ENABLE_DIARIZATION_KEY    - specify whether to diarize as well as transcribe
#     HF_TOKEN_KEY              - Hugging Face (HF) authentication token for using models hosted on HF
#     MODEL_SIZE_KEY            - The Whisper model to use - 'tiny', 'base', 'small', 'medium', 'large'
#     OUTPUT_DIR_KEY            - directory for output from the program
#     ENABLE_OVERWRITE_KEY      - specify whether to overwrite transcription and diarization outputs, if present
#     ENABLE_LOGFILE_KEY        - whether to write to a log file
#     LOGFILE_DIR_KEY           - logfile directory
#     LOGFILE_NAME_KEY          - logfile name
#     PERFORMANCE_LOG_NAME_KEY  - name of the performance log

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
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', ''):
        return True
    return False

def parse_command_line_args():
    """
    Parse command line arguments and return the parsed arguments.

    Returns:
        dict: Parsed command line arguments as a dictionary.
    """
    parser = argparse.ArgumentParser( description="Process command-line arguments for audio transcription." )
    #
    parser.add_argument("-au", "--audio_file",           help="The input audio file or file directory",   dest=CONST.INFILE_KEY, required=True)
    parser.add_argument("-cx", "--config_processor",     help="An alternative xml config file",           dest=CONST.CONFIG_FILE_KEY)
    parser.add_argument("-bs", "--batch_size",           help="The batch size for transcription",         dest=CONST.BATCH_SIZE_KEY)
    parser.add_argument("-ct", "--compute_type",         help="Specifies the computation type",           dest=CONST.COMPUTE_TYPE_KEY)
    parser.add_argument("-dv", "--device",               help="Hardware device for diarization",          dest=CONST.DEVICE_KEY)
    parser.add_argument("-ed", "--enable_diarization",   help="If true, diarize after transcription",     dest=CONST.ENABLE_DIARIZATION_KEY, type=str2bool, const=True, default=None, nargs='?' )
    parser.add_argument('-el', '--enable_logfile',       help="If true, enable logfile output",           dest=CONST.ENABLE_LOGFILE_KEY,     type=str2bool, const=True, default=None, nargs='?' )
    parser.add_argument("-ht", "--hf_token",             help="The user token needed for diarization",    dest=CONST.HF_TOKEN_KEY)
    parser.add_argument("-ld", "--logfile_dir",          help="Log file to which to writen",              dest=CONST.LOGFILE_DIR_KEY)
    parser.add_argument("-ln", "--logfile_name",         help="Directory for storing the log file",       dest=CONST.LOGFILE_NAME_KEY)
    parser.add_argument("-ms", "--model_size",           help="The model size for transcription",         dest=CONST.MODEL_SIZE_KEY)
    parser.add_argument("-od", "--output_dir",           help="Directory for storing the transcript",     dest=CONST.OUTPUT_DIR_KEY)
    parser.add_argument('-ov', '--enable_overwrite',     help="If true, overwrite any earlier output",    dest=CONST.ENABLE_OVERWRITE_KEY,   type=str2bool, const=True, default=None, nargs='?' )
    parser.add_argument("-lp", "--performance_log_name", help="Name for the performance log file",        dest=CONST.PERFORMANCE_LOG_NAME_KEY)
    
    try:
        return vars(parser.parse_args())
    except Exception as e:
        print( STATUS.errmsg( "\nparse_command_line_args: " + STATUS.err_to_str(e) + ' - exiting ', True ), file=sys.stderr )
        sys.exit(STATUS.ExitStatus.command_line_error())
