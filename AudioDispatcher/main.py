# *************************************************************************************************************************
#   main.py
#     Entry point for the WhisperX-based audio transcription application.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio_path [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#      Arguments and defaults:
#         -au, --audio_path [path] : Path to the audio file or directory for transcription
#         -bs, --batch_size [size] :  Batch size for transcription
#         -cx, --configxml [path] : XML configuration file. Default is 'config/default_config.xml'
#         -ct, --compute_type : The computation type
#         -dv, --device : hardware device for diarization.  Defaults to 'cpu'
#         -el, --enable-logfile : If included, write log messages to log file, as well as console.
#         -ht, --hf_token [token] : Hugging Face token for model access with diarization.  Defaults to None.
#         -lf, --logfile [path] : Name of log file to which to write.  Defaults to sys.stderr.
#         -ms, --model_size [size] : Whisper model size for transcription. Defaults to 'base'.
#         -od, --output_dir [dir] : Directory to store transcription files. Defaults to 'transcriptions'.
#      Outputs:
#         Processes and transcribes audio files, outputting transcription files in the specified directory.
#         Application activity and errors are logged.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  March 1 2024
#   authors:       Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# sys –
#   exit – exit, returning a final status code

import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# DEFAULTS - supporting definitions for forms parsing
#   CONFIG_FILE -         XML file for overriding selected default values
#   CONFIG_FILE_SCHEMA -  XML file for validating configuration files
# ISCLogWrapper - wrapper for logging functionalities
#   ISCLogWrapper - class to configure and initiate logging
#   logging.getLogger - method to return a logger instance with the specified name
# TranscriptionConfig - configuration handler for transcription settings
#   TranscriptionConfig - class to manage transcription configuration from an XML file
# WhisperxTranscriber - package for the transcription model
#   WhisperxTranscriber - class to handle transcription process using Whisper models

import src.StatusManager as STATUS
from src.TranscriptionConfig import TranscriptionConfig
from src.WhisperxTranscriber import WhisperxTranscriber

# ***********************************************
# program main
# ***********************************************

if __name__ == '__main__':

    # Configure program execution.
    config = TranscriptionConfig()
    logger = config.logger()

    # Transcribe the input
    try:
        model = WhisperxTranscriber(config, logger)
        model.transcribe()
        status_msg = STATUS.statusmsg('Processing completed.')
        logger.info(status_msg)
        sys.exit(STATUS.ExitStatus.status)
    except Exception as e:
        err_msg = STATUS.errmsg(f'?? exiting: {STATUS.err_to_str(e)}')
        logger.error(err_msg)
        sys.exit(STATUS.ExitStatus.uncertain_error())
