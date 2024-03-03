# *************************************************************************************************************************
#   WhisperxTranscriber.py – Transcribe and diarize recordings
# *************************************************************************************************************************
#
#   Usage:
#       This module contains the WhisperxTranscriber class, which uses the WhisperX speech recognition library to transcribe
#       and optionally diarize
#       audio files. WhisperX is a third party library that augments OpenAI's transcription library,
#       Whisper, with support for diarization.  
# -------------------------------------------------------------------------------------------------------------------------#
#   Usage:
#      from WhisperxTranscriber import WhisperxTranscriber
#      transcriber = WhisperxTranscriber(model_size='base', hf_token='your_hf_token', audio_path='path_to_audio_or_directory')
#      transcriber.transcribe()
#
#      Parameters:     
#        audio_path (str): The path to the audio file or directory containing audio files to transcribe.
#        batch_size (int): The number of audio segments to process simultaneously.
#        compute_type (str): The type of computation (precision) to use, such as 'int8' or 'float16'.
#        device (str): Device to support ('cpu' by default).
#        enable_diarization (bool): Specify whether to diarize as well as transcribe (True by default).
#        hf_token (str): Hugging Face authentication token for using models hosted on Hugging Face.
#        model_size (str): The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
#        output_dir (str): The path to store transcriptions in.
#        logger (logging.Logger)za: Logging object for capturing status messages.
#        model: The loaded Whisper model.
#
#      Outputs:
#         A text file for each input audio file, containing the transcribed text with timestamps and speaker identification.
#         When a directory is provided, it will transcribe all supported audio files within that directory.
#
#   Design and Implementation Notes:
#   -.  The WhisperxTranscriber uses WhisperX, a library isthat is downloadable  available from at https://github.com/m-bain/
#       -.  WhisperX isWhisperX is a third party library that augments OpenAI's transcription library,
#       Whisper transcription service, withto support for diarization.
#            -.  It features a diarization pipeline to distinguish between#  different speakers within the audio.
#            -.  Outputs include aligned segments with speaker labels to enhance transcript readability.
#       -.  To access it, Users of WhisperX prospective users must create an account at that URL and requestobtain a keya token.
#   -.  The WhisperxTranscriber is optimized for CPU usage by default but can be configured for GPU.
#   -.  It features a diarization pipeline to distinguish between#  different speakers within the audio.
#   -.  Outputs include aligned segments with speaker labels to enhance transcript readability.

# -------------------------------------------------------------------------------------------------------------------------
#   last updated: 1 March 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ==============================================================================================
#  Python standard library
# ==============================================================================================
#
# logging - logging library
#    basicConfig - function to configure the logging
#    getLogger - function to get a logging instance
# os - operating system interface
#    path.basename - get the base name of pathname
#    path.splitext - split the pathname into a pair (root, ext)
# time - 
#    ctime - returns current time of day

import logging
import os
import time

# ==============================================================================================
#   custom
# ==============================================================================================
#
# StatusManager - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status

import src.StatusManager as STATUS
from src.IscFileSearch import IscFileSearch

# ==============================================================================================
# other external
# ==============================================================================================

#  TODO ADD Transcribe engine support

# ***************************************************************************************************************************
#  logging support
# ***************************************************************************************************************************

# Setup logger for informational messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WhisperxTranscriber')

class WhisperxTranscriber:
    """
    The WhisperxTranscriber class utilizes the WhisperX library to transcribe and optionally diarize audio recordings.

    Attributes:
        audio_file (str): The audio file to transcribe.
        batch_size (int): The number of audio segments to process simultaneously.
        compute_type (str): The type of computation (precision) to use, such as 'int8' or 'float16'.
        device (str): Device to support ('cpu' by default).
        enable_diarization (bool): Specify whether to diarize as well as transcribe (True by default).
        hf_token (str): Hugging Face authentication token for using models hosted on Hugging Face.
        model_size (str): The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
        output_dir (str): The path to store transcriptions in.
        logger (logging.Logger): Logging object for capturing status messages.
        model: The loaded Whisper model.

    Methods:
        transcribe(): Transcribe audio files with optional diarization.
        diarize_and_write(output_dir, output_filename, result, audio): Diarize the audio file and write the transcription.
        transcribe_and_write(output_dir, output_filename, result): Transcribe the audio file and write the transcription.
        write_transcription(output_dir, output_filename, result): Write the transcription to the specified output directory and filename.
    
    """

    def __init__(self, config_dict, logger):
        """
        Initialize the WhisperxTranscriber with specified configuration.

        Args:
            config_dict (dict): object with a get() method for accessing parameters.
            logger (logging.Logger): Logging object for capturing status messages.
        """
        # Set operating parameters
        self.audio_path = config_dict.get('audio_path')
        self.model_size = config_dict.get('model_size')
        self.output_dir = config_dict.get('output_dir')
        self.logger = logger

        # Set file name for specific status message 
        STATUS.statusmsg.filename= self.audio_path
        STATUS.errmsg.filename= self.audio_path
        print("################################################################")

    def transcribe(self):
        """
        Transcribe audio files with optional diarization.
        """
        self.logger.info(f"Transcribing with {self.model_size} model")

        try:
            start_time = time.time()
            if os.path.isdir(self.audio_path):
                self.logger.info("Traversing if audio_path is a directory")
                file_search = IscFileSearch(self.audio_path)
                audio_path = file_search.traverse_directory()
            else:
                audio_path = [self.audio_path]

            for audio in audio_path:
                print("Current audio file", audio)
            end_time = time.time()
            self.total_elapsed_time = (end_time - start_time) / 60
            self.logger.info(f"Total elapsed time for all audio files: {self.total_elapsed_time} minutes")

        except Exception as e:
            self.logger.critical(f"Error during {'diarization' if self.enable_diarization else 'transcription'}: {STATUS.err_to_st(e)}")
