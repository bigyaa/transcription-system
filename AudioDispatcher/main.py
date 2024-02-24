# *************************************************************************************************************************
#   main.py 
#     Entry point for the WhisperX-based audio transcription application. 
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#      Arguments and defaults:
#         -au, --audio [dir or path] : Path to the audio file or directory for transcription.
#         -cx, --configxml [path] : XML configuration file. Default is 'config/default_config.xml'
#         -dv. --device : hardware device for diarization.  Defaults to 'cpu'
#         -ex, --extensions [ext] : List of allowed audio file extensions. Defaults to ['.mp3', '.wav', '.aac'].
#         -ht, --hf_token [token] : Hugging Face token for model access with diarization.  Defaults to None.
#         -lf, --logfile [path] : Name of log file to which to write.  Defaults to sys.stderr.
#         -mt, --model_type [type] : Whisper model type for transcription. Defaults to 'base'.
#         -od, --output_dir [dir] : Directory to store transcription files. Defaults to 'transcriptions'.
#      Outputs:
#         Processes and transcribes audio files, outputting transcription files in the specified directory.
#         Application activity and errors are logged.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  January 2024
#   authors:       Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# program constants
# ***********************************************
#  PROGRAM EXIT CODES

SUCCESS = 0
FAILURE = 1

# ***********************************************
# imports
# ***********************************************

# sys –
#   exit – exit, returning a final status code
# threading - 
#    current_thread - identify current thread

import sys
import threading

# Custom packages for the transcription model and utilities
#
# src.transcribe.models.WhisperxTranscriber - custom package for the transcription model
#   WhisperxTranscriber - class to handle transcription process using Whisper models
# src.utils.ISCLogWrapper - custom wrapper for logging functionalities
#   ISCLogWrapper - class to configure and initiate logging
#   logging.getLogger - method to return a logger instance with the specified name
# src.utils.TranscriptionConfig - custom configuration handler for transcription settings
#   TranscriptionConfig - class to manage transcription configuration from an XML file
# src.utils.IscFileSearch - module for searching and handling files within directories
#   IscFileSearch - class for searching files and performing file operations in a specified directory

from src.transcribe.models.WhisperxTranscriber import WhisperxTranscriber
from src.utils.ISCLogWrapper import ISCLogWrapper, logging
from src.utils.TranscriptionConfig import TranscriptionConfig
from src.utils.helperFunctions import format_error_message 


# ***********************************************
# program main
# ***********************************************

if __name__ == '__main__':

    # Configure program execution.

    config = TranscriptionConfig()

    # Configure logging for the application.

    isc_log_wrapper = ISCLogWrapper(config)
    if not isc_log_wrapper.set_up_logging():
        print(f"?? {threading.current_thread().name}: Failed to set up logging, aborting.")
        sys.exit(FAILURE)
    logger = logging.getLogger(__name__)

    try:
        model = WhisperxTranscriber(config, logger)
        model.transcribe() 
        logger.info(f"Processing of {config.get('audiodir')} completed. ") 
        sys.exit(SUCCESS)
    except Exception as e:
        logger.critical(f"Processing of {config.get('audiodir')} failed due to error: {format_error_message(e)}")
        sys.exit(FAILURE)
