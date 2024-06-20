# *************************************************************************************************************************
#   Transcribe.py – Transcribe and diarize recordings
# *************************************************************************************************************************
#
#   Usage:
#       This module contains the Transcribe function, which calls the CoreAudioProcessor module that uses the WhisperX speech recognition library to transcribe
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
#   last updated: 3 March 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ==============================================================================================
#  Python standard library
# ==============================================================================================
#
# os - operating system interface
#    path.basename - get the base name of pathname
#    path.splitext - split the pathname into a pair (root, ext)
# time -
#    ctime - returns current time of day

import logging
import os
import subprocess
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

# Setup logger for informational messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhisperxTranscriber")


def Transcribe(config_dict, logger):
    """
    Initialize the CoreAudioProcessor with specified configuration.

    Args:
        config_dict (dict): object with a get() method for accessing parameters.
        logger (logging.Logger): Logging object for capturing status messages.
    """
    # Set operating parameters
    audio_path = config_dict.get("audio_path")
    model_size = config_dict.get("model_size")
    enable_diarization = config_dict.get("enable_diarization")
    flags = {
        "-cx": config_dict.get("configxml"),
        "-bs": config_dict.get("batch_size"),
        "-ct": config_dict.get("compute_type"),
        "-dv": config_dict.get("device"),
        "-ed": config_dict.get("enable_diarization"),
        "-el": config_dict.get("enable_logfile"),
        "-ht": config_dict.get("hf_token"),
        "-ms": config_dict.get("model_size"),
        "-od": config_dict.get("output_dir"),
    }
    logger = logger

    # Set file name for specific status message
    STATUS.statusmsg.filename = audio_path
    STATUS.errmsg.filename = audio_path

    logger.info(f"Transcribing with {model_size} model")

    try:
        start_time = time.time()
        audio_paths = [audio_path] if not os.path.isdir(
            audio_path) else IscFileSearch(audio_path).traverse_directory()

        main_script_path = os.path.abspath("CoreAudioProcessor/main.py")
        python_interpreter = "/usr/local/bin/python3"
        failure_counter = 0
        for audio in audio_paths:
            logger.info(f"Processing audio file: {audio}")
            try:
                process_start_time = time.time()
                subprocess.run(
                    [python_interpreter, main_script_path, "-au", audio] +
                    [f"{flag}={value}" for flag, value in flags.items()],
                    capture_output=True,
                    check=True  # Raises CalledProcessError for non-zero exit status
                )
                process_end_time = time.time()
                process_elapsed_time = process_end_time - process_start_time
                logger.info(
                    f"Run time for {audio}: {process_elapsed_time} seconds")
                logger.info(f"Processing of {audio} completed successfully.")
                failure_counter = 0
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
                failure_counter += 1
                if failure_counter >= 5:
                    logger.error("Exceeded maximum failure limit. Exiting.")
                    break
            except Exception as e:
                logger.error(
                    f"Exception occurred during processing {audio}: {e}")
                failure_counter += 1
                if failure_counter >= 5:
                    logger.error("Exceeded maximum failure limit. Exiting.")
                    break

        end_time = time.time()
        total_elapsed_time = (end_time - start_time) / 60
        logger.info(
            f"Total elapsed time for all audio files: {total_elapsed_time} minutes")

    except Exception as e:
        logger.critical(
            f"Error during {'diarization' if enable_diarization else 'transcription'}: {STATUS.err_to_str(e)}")
