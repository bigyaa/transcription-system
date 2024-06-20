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
#      transcriber = WhisperxTranscriber(model_size='base', hf_token='your_hf_token', audio_files='path_to_audio_or_directory')
#      transcriber.transcribe()
#
#      Parameters:     
#        audio_files (str): The path to the audio file or directory containing audio files to transcribe.
#        batch_size (int): The number of audio segments to process simultaneously.
#        compute_type (str): The type of computation (precision) to use, such as 'int8' or 'float16'.
#        device (str): Device to support ('cpu' by default).
#        enable_diarization (bool): Specify whether to diarize as well as transcribe (True by default).
#        hf_token (str): Hugging Face authentication token for using models hosted on Hugging Face.
#        model_size (str): The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
#        output_dir (str): The path to store transcriptions in.
#        logger (logging.Logger): Logging object for capturing status messages.
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
#   authors: Ruben Maharjan, Bigya Bajarcharya, Phil Pfeiffer
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
# pathlib - File system path manipulation
#    PurePath.parts - split file path into constituent segments
# sys –
#   exit – exit, returning a final status code
#   stderr – the standard error message stream
# time - 
#    ctime - returns current time of day

import logging
import os
import pathlib
import sys
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

# ==============================================================================================
# other external
# ==============================================================================================

# whisperx - speech recognition library with diarization support
#    load_audio - function to load audio files into memory
#    DiarizationPipeline - class for performing speaker diarization
#    load_align_model - function to load alignment model
#    align - function to align transcriptions with audio
#    assign_word_speakers - function to assign speakers to words

try:
    import whisperx
except:
    err_msg = f"\nwhisperx not yet installed - execute pip install whisperx, then rerun this program"
    print( STATUS.errmsg( err_msg, True ), file=sys.stderr )
    sys.exit(STATUS.ExitStatus.command_line_error())

from whisperx import (DiarizationPipeline, load_audio, load_align_model, load_model, align, assign_word_speakers)


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
        self.audio_file = config_dict.get('audio_file')
        self.batch_size = int(config_dict.get('batch_size'))
        self.compute_type = config_dict.get('compute_type')
        self.device = config_dict.get('device')
        self.enable_diarization = config_dict.get('enable_diarization')
        self.hf_token = config_dict.get('hf_token')
        self.model_size = config_dict.get('model_size')
        self.output_dir = config_dict.get('output_dir')
        self.logger = logger

        # Set file name for specific status message 
        STATUS.statusmsg.filename= self.audio_file
        STATUS.errmsg.filename= self.audio_file

        # Set up operations
        self.logger.info(f"Loading {self.model_size} model")
        try:
            self.model = load_model(self.model_size, self.device, compute_type=self.compute_type)
        except Exception as e:
            err_msg = f"Error while loading whisper model:\n {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )

    def transcribe(self):
        """
        Transcribe audio files with optional diarization.
        """
        self.logger.info(f"Transcribing with {self.model_size} model")

        try:
            start_time = time.time()
            audio = self.audio_file

            if os.path.isdir(audio):
                self.logger.error( STATUS.errmsg( "This function does not accept a directory." ) )
                sys.exit(STATUS.ExitStatus.internal_error())

            self.logger.info(f"{'Diarizing' if self.enable_diarization else 'Transcribing'} audio file: {audio}")
            audio_start_time = time.time()
            waveform = load_audio(audio)
            result = self.model.transcribe(waveform, batch_size=self.batch_size)

            audio_path = os.path.abspath(audio)
            p = pathlib.PurePath(audio_path)
            # Check if there are at least one parent directory
            if len(p.parents) >= 1:
                output_dir = str(p.parents[0])
            else:
                # Handle the case when there are no parent directories
                output_dir = ""

            # Check if the output_dir is not empty and the output_dir.split('.') has at least two elements
            if output_dir and len(self.output_dir.split('.')) >= 2:
                output_dir += self.output_dir.split('.')[1]

            base_name = p.name.split('.')[0] + '.txt'
            output_filename = os.path.join(output_dir, base_name)
            audio_end_time = time.time()
            self.audio_elapsed_time = (audio_end_time - audio_start_time) / 60

            if self.enable_diarization:
                self.diarize_and_write(output_dir, output_filename, result, audio)
            else:
                self.transcribe_and_write(output_dir, output_filename, result)
            end_time = time.time()
            self.total_elapsed_time = (end_time - start_time) / 60
            self.logger.info(f"Total elapsed time for the audio file: {self.total_elapsed_time} minutes")
        except Exception as e:
            err_msg = f"Error during {'diarization' if self.enable_diarization else 'transcription'}: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )

    def diarize_and_write(self, output_dir, output_filename, result, audio):
        """
        Diarize the audio file and write the transcription.

        Args:
            output_dir (str): The output directory.
            output_filename (str): The output filename.
            result (dict): Result from transcribing the audio file.
            audio (str): The path to the audio file.
        """
        try:
            self.logger.info(f"Diarizing audio file: {audio}")

            diarize_model = DiarizationPipeline(use_auth_token=self.hf_token, device=self.device)
            diarize_segments = diarize_model(audio)

            model_a, metadata = load_align_model(language_code=result["language"], device=self.device)

            aligned_segments = align(result['segments'], model_a, metadata, audio, self.device, return_char_alignments=False)
            segments_with_speakers = assign_word_speakers(diarize_segments, aligned_segments)

            self.write_transcription(output_dir, output_filename, segments_with_speakers)

        except Exception as e:
            err_msg = f"Error while diarizing: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )

    def transcribe_and_write(self, output_dir, output_filename, result):
        """
        Transcribe the audio file and write the transcription.

        Args:
            output_dir (str): The output directory.
            output_filename (str): The output filename.
            result (dict): Result from transcribing the audio file.
        """
        try:
            model = load_model(self.model_size, self.device, compute_type=self.compute_type)

            self.write_transcription(output_dir, output_filename, result)

        except Exception as e:
            err_msg = f"Error during transcription: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )

    def write_transcription(self, output_dir, output_filename, result):
        """
        Write the transcription to the specified output directory and filename.

        Args:
            output_dir (str): The output directory.
            output_filename (str): The output filename.
            result (dict): Result from transcribing the audio file.
        """
        try:
            if not os.path.exists(output_dir):  os.makedirs(output_dir)
            if not os.path.exists(output_filename):
                with open(output_filename, "w") as output_file:
                    output_file.write(f"Time taken to transcribe/diarize: {self.audio_elapsed_time} minutes\n\n")
                    for segment in result["segments"]:
                        output_file.write(
                            f"[{segment['start']} - {segment['end']}] {segment['speaker'] + ' : ' if self.enable_diarization else ''} {segment['text']}\n")
            else:
                self.logger.info(f"Transcription of {output_filename} already exists.")
            self.logger.info(f"Finished writing {'diarization' if self.enable_diarization else 'transcription'} to file: {output_filename}")

        except Exception as e:
            err_msg = f"Error during {'diarization' if self.enable_diarization else 'transcription'}: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )
