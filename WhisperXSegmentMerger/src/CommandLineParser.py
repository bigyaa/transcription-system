# *************************************************************************************************************************
#   CommandLineParser.py
#       Provide command-line parsing for the WhisperX segment merging application.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       Call parse_command_line_args() to parse and retrieve command-line arguments.
#
#       Parameters:
#           Command-line parameters are supported for specifying a transcript, configuration XML, outputs,
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
#   author:  Phil Pfeiffer
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
#     CONFIG_FILE_KEY      - XML file for overriding selected default values
#     INFILE_KEY           - input to transcribe
#     OUTPUT_DIR_KEY       - directory for output from the program
#     OUTPUT_FILE_KEY      - file name for program output
#     ENABLE_LOGFILE_KEY   - whether to write to a log file
#     LOGFILE_DIR_KEY      - logfile directory
#     LOGFILE_NAME_KEY     - logfile name

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
    parser.add_argument("-tr", "--transcript",       help="The transcript to process",       dest=CONST.INFILE_KEY, required=True)
    parser.add_argument("-cx", "--config_processor", help="An alternative xml config file",  dest=CONST.CONFIG_FILE_KEY)
    parser.add_argument('-el', '--enable_logfile',   help="If true, enable logfile output",  dest=CONST.ENABLE_LOGFILE_KEY,     type=str2bool, const=True, default=None, nargs='?' )
    parser.add_argument("-ld", "--logfile_dir",      help="Log file to which to writen",         dest=CONST.LOGFILE_DIR_KEY)
    parser.add_argument("-ln", "--logfile_name",     help="Directory for storing the log file",  dest=CONST.LOGFILE_NAME_KEY)
    parser.add_argument("-od", "--output_dir",       help="Directory for storing the updated transcript", dest=CONST.OUTPUT_DIR_KEY)
    parser.add_argument("-of", "--output_file",      help="File for capturing the updated transcript",    dest=CONST.OUTPUT_FILE_KEY)
    
    try:
        return vars(parser.parse_args())
    except Exception as e:
        print( STATUS.errmsg( "\nparse_command_line_args: " + STATUS.err_to_str(e) + ' - exiting ', True ), file=sys.stderr )
        sys.exit(STATUS.ExitStatus.command_line_error())
