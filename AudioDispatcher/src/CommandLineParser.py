# *************************************************************************************************************************
#   CommandLineParser.py
#       Provide command-line parsing for an audio transcription application.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       Call parse_command_line_args() to parse and retrieve command-line arguments.
#       Use validate_configxml(xml_file, xsd_file) to validate an XML configuration against an XSD schema.
#
#       Parameters:
#           Command-line parameters are supported for specifying audio files, configuration XML, model type,
#           directories for audio files and transcriptions, user tokens for diarization, and allowed file extensions.
#
#       Outputs:
#           Command-line parsing results in a namespace of parsed arguments.
#
#   Design Notes:
#   -.  The module is designed to be used as a utility in a larger audio transcription application.
#   -.  Logging is configured to provide info and critical feedback for the operations performed.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  3 March 2024
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

import src.StatusManager as STATUS


# ***********************************************
#  helper functions proper
# ***********************************************

def str2bool(v):
    """
    Convert a string to a boolean value.

    Args:
        v (str): The input string.

    Returns:
        bool: The corresponding boolean value.

    Raises:
        argparse.ArgumentTypeError: If the input string is not a valid boolean representation.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_command_line_args():
    """
    Parse command line arguments and return the parsed arguments.

    Returns:
        dict: Parsed command line arguments as a dictionary.
    """
    parser = argparse.ArgumentParser( description="Process command-line arguments for audio transcription." )
    #
    parser.add_argument("-au", "--audio_path",         help="The input audio file or file directory", dest='audio_path', required=True) 
    parser.add_argument("-bs", "--batch_size",         help="The batch size for transcription", dest="batch_size")
    parser.add_argument("-cx", "--configxml",          help="An alternative xml config file", dest='configxml')
    parser.add_argument("-ct", "--compute_type",       help="Specifies the computation type", dest='compute_type')
    parser.add_argument("-dv", "--device",             help="Hardware device for diarization", dest='device')
    parser.add_argument("-ed", "--enable_diarization", help="If true, diarize after transcription", dest="enable_diarization", const='True', choices=['True', 'False'], nargs='?' )
    parser.add_argument('-el', '--enable_logfile',     help="If true, enable logfile output", dest="enable_logfile", const='True', choices=['True', 'False'], nargs='?' )
    parser.add_argument("-ht", "--hf_token",           help="The user token needed for diarization", dest="hf_token")
    parser.add_argument("-lf", "--logfile",            help="Log file to which to writen", dest="logfile")
    parser.add_argument("-ms", "--model_size",         help="The model size for transcription", dest="model_size")
    parser.add_argument("-od", "--output_dir",         help="The directory to store transcriptions", dest="output_dir")
    
    try:
        return vars(parser.parse_args())
    except Exception as e:
        print( STATUS.errmsg( "\nparse_command_line_args: " + STATUS.err_to_str(e) + ' - exiting ', True ), file=sys.stderr )
        sys.exit(STATUS.ExitStatus.command_line_error())
