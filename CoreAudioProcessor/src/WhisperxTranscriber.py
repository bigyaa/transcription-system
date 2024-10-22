# *************************************************************************************************************************
#   WhisperxTranscriber.py – Transcribe and diarize recordings
# *************************************************************************************************************************
#   About:
#       This module contains the WhisperxTranscriber class, which uses the WhisperX speech recognition library to transcribe
#       and optionally diarize audio files. WhisperX is a third party library that augments OpenAI's transcription library,
#       Whisper, with support for diarization.
#
#   Usage:
#      from WhisperxTranscriber import WhisperxTranscriber
#      transcriber = WhisperxTranscriber(model_size='base', hf_token='your_hf_token', audio_files='path_to_audio_or_directory')
#      transcriber.transcribe()
#
#   Parameters:
#      keys in config_dict:
#        audio_files (str): The path to the audio file or directory containing audio files to transcribe.
#        batch_size (int): The number of audio segments to process simultaneously.
#        compute_type (str): The type of computation (precision) to use, such as 'int8' or 'float16'.
#        device (str): Device to support ('cpu' by default).
#        enable_diarization (bool): If True (default), diarize as well as transcribe
#        hf_token (str): Hugging Face authentication token for using models hosted on Hugging Face.
#        model_size (str): The size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
#        output_dir (str): The path to store transcriptions in.
#        overwrite (bool): If True (default), overwrite existing transcription or diarization, if present
#      logger (logging.Logger): Logging object for capturing status messages.
#
#   Outputs:
#      A text file for the input audio file, containing the transcribed text with timestamps and speaker identification.
# -------------------------------------------------------------------------------------------------------------------------
#   Design and Implementation Notes:
#   -.  Transcribe() uses WhisperX, a library is that is downloadable  available from at https://github.com/m-bain/
#       -.  WhisperX is a third party library that augments OpenAI's transcription library,
#           Whisper transcription service, with support for diarization.
#           -.  It features a diarization pipeline to distinguish between different speakers within the audio.
#           -.  It labels Whisper segments with speaker tags to enhance transcript readability.
#      -.  To access it, Users of WhisperX prospective users must create an account at that URL and request a key token.
# -------------------------------------------------------------------------------------------------------------------------
#   last updated: 20 May 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ==============================================================================================
#  Python standard library
# ==============================================================================================
#
# pathlib - File system path manipulation
#    PurePath.parts - split file path into constituent segments
# sys –
#   exit – exit, returning a final status code
#   stderr – the standard error message stream
# time -
#    ctime - returns current time of day

from pathlib import Path
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
# CONSTANTS - supporting definitions for program operation
#   shared designations for configurable parameters
#     INFILE_KEY              - input to transcribe
#     BATCH_SIZE_KEY          - Number of audio segments to process simultaneously
#     COMPUTE_TYPE_KEY        - Type of computation (precision) to use, such as 'int8' or 'float16'
#     DEVICE_KEY              - Type of hardware device to use; either 'cpu' or 'gpu'
#     ENABLE_DIARIZATION_KEY  - specify whether to diarize as well as transcribe
#     HF_TOKEN_KEY            - Hugging Face (HF) authentication token for using models hosted on HF
#     MODEL_SIZE_KEY          - The Whisper model to use - 'tiny', 'base', 'small', 'medium', 'large'
#     OUTPUT_DIR_KEY          - directory for output from the program
#     INFILE_SIZE_KEY         - the input file's size
#     OUTPUT_FILE_KEY         - the transcription file's name
#     ENABLE_OVERWRITE_KEY    - specify whether to overwrite transcription and diarization outputs, if present
#     OUTCOME_KEY             - natural language characterization of overall process outcome
#     TRANSCRIPTION_TIME_KEY  - time to transcribe input
#     DIARIZATION_TIME_KEY    - time to diarize input
#     TOTAL_TIME_KEY          - total time for execution
#     TOTAL_SEGMENT_COUNT_KEY - count of segments
#     BAD_SEGMENT_COUNT_KEY   - count of bad segments

import src.StatusManager as STATUS
import src.CONSTANTS     as CONST


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

n_min = lambda elapsed_t: round(elapsed_t)//60
n_sec = lambda elapsed_t: round(elapsed_t)%60
normalized_time = lambda start, end: {CONST.MINUTES_KEY: n_min(end-start), CONST.SECONDS_KEY: n_sec(end-start)}

def elapsed_time(start_time, end_time):
    elapsed_t = end_time - start_time
    elapsed_min = '' if not n_min(elapsed_t) else f'{n_min(elapsed_t)} min'
    elapsed_sec = '' if not n_sec(elapsed_t) else f'{n_sec(elapsed_t)} sec'
    elapsed_min_sec = ', '.join( [s for s in [elapsed_min, elapsed_sec ] if s != '' ] )
    if not elapsed_min_sec:  elapsed_min_sec = '<1 sec'
    return elapsed_min_sec

class WhisperxTranscriber:
    """
    The WhisperxTranscriber class uses the WhisperX library to transcribe and optionally diarize audio recordings.

    Attributes:

    Methods:
        __init__(config_dict, logger):  initialize class instance
            config_dict: parameters for WhisperX initialization
            logger: logging object
        transcribe(): Transcribe audio files with optional diarization.
        diarize(output_dir, output_filename, result, audio): Diarize the audio file and write the transcription.
        transcribe(output_dir, output_filename, result): Transcribe the audio file and write the transcription.
        write_result(output_dir, output_filename, result): Write the transcription to the specified output directory and filename.
    """

    def __init__(self, config_dict, logger):
        """
        Initialize the WhisperxTranscriber with specified configuration.

        Args:
            config_dict (dict): object with a get() method for accessing parameters.
            logger (logging.Logger): Logging object for capturing status messages.
        """
        # Set operating parameters
        self.audio_file = config_dict.get(CONST.INFILE_KEY)
        self.batch_size = int(config_dict.get(CONST.BATCH_SIZE_KEY))
        self.compute_type = config_dict.get(CONST.COMPUTE_TYPE_KEY)
        self.device = config_dict.get(CONST.DEVICE_KEY)
        self.enable_diarization = config_dict.get(CONST.ENABLE_DIARIZATION_KEY)
        self.hf_token = config_dict.get(CONST.HF_TOKEN_KEY)
        self.model_size = config_dict.get(CONST.MODEL_SIZE_KEY)
        self.output_dir_abspath = str(Path(config_dict.get(CONST.OUTPUT_DIR_KEY)).absolute())
        self.enable_overwrite = config_dict.get(CONST.ENABLE_OVERWRITE_KEY)
        self.logger = logger

        # Set file name for specific status message
        STATUS.statusmsg.filename= self.audio_file
        STATUS.errmsg.filename= self.audio_file

        # Set up operations
        self.performance_data = CONST.null_transcription_data()
        self.audio_file_abspath = str(Path(self.audio_file).absolute())
        self.performance_data[CONST.INFILE_KEY] = self.audio_file_abspath
        self.performance_data[CONST.INFILE_SIZE_KEY] = Path(self.audio_file_abspath).stat().st_size

    def transcribe(self):
        """
        Transcribe audio files with optional diarization.
        """
        overall_start_time = time.time()

        if not Path(self.audio_file_abspath).is_file():
            STATUS.ExitStatus.file_type_error()
            process = 'diarize' if self.enable_diarization else 'transcribe'
            err_msg = f"Item to {process} ({self.audio_file}) wasn't a file"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return self.performance_data

        this_filename = Path(self.audio_file).name
        self.output_filename = str(Path(self.output_dir_abspath, this_filename).with_suffix('.txt'))
        self.performance_data[CONST.OUTPUT_FILE_KEY] = self.output_filename

        if (not self.enable_overwrite) and Path(self.output_filename).exists():
            syndrome = f"{self.output_filename} already exists - not overwritten."
            self.logger.info( syndrome )
            self.performance_data[CONST.OUTCOME_KEY] = syndrome
            return self.performance_data

        # loading the model takes time - delay this action until we've committed to transcribing this recording
        self.logger.info(f"Loading {self.model_size} model")
        try:
            self.model = load_model(self.model_size, self.device, compute_type=self.compute_type)
        except Exception as e:
            err_msg = f"Error while loading whisper model:\n {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            STATUS.ExitStatus.internal_error()
            raise STATUS.InternalError( err_msg )

        processing = ' and diarizing' if self.enable_diarization else ''
        self.logger.info(f" Transcribing{processing} audio file {self.audio_file} with {self.model_size} model")
        transcription_start_time = time.time()
        process = 'diarization' if self.enable_diarization else 'transcription'

        try:
            waveform = load_audio(self.audio_file_abspath)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Load audio error during {process} for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return self.performance_data

        try:
            intermediate_result = self.model.transcribe(waveform, batch_size=self.batch_size)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Transcription error during {process} for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return self.performance_data

        end_time = time.time()
        self.logger.info( f"Transcription successful. time to transcribe: {elapsed_time(transcription_start_time, end_time)}")
        self.performance_data[CONST.TRANSCRIPTION_TIME_KEY] = normalized_time(transcription_start_time, end_time)

        if self.enable_diarization:
            if not ( result := self.diarize(intermediate_result) ):
                return self.performance_data
        else:
            result = intermediate_result

        if self.write_result( result ):
            self.performance_data[CONST.OUTCOME_KEY] = 'success'

        end_time = time.time()
        self.performance_data[CONST.TOTAL_TIME_KEY] = normalized_time(overall_start_time, end_time)
        return self.performance_data

    def diarize(self, result):
        """
        Diarize the audio file,generating the output
        """
        diarization_start_time = time.time()
        try:
            diarize_model = DiarizationPipeline(use_auth_token=self.hf_token, device=self.device)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Pipeline error during diarization for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return None

        try:
            diarize_segments = diarize_model(self.audio_file_abspath)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Segmentation error during diarization for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return None

        try:
            model_a, metadata = load_align_model(language_code=result["language"], device=self.device)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Alignment model error during diarization for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return None

        try:
            aligned_segments = align(result['segments'], model_a, metadata, self.audio_file_abspath, self.device, return_char_alignments=False)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = f" Alignment error during diarization for file {self.audio_file_abspath}"
            err_msg += f"\n Syndrome: {STATUS.err_to_str(e)}"
            self.logger.error( STATUS.errmsg( err_msg ) )
            return None

        end_time = time.time()
        self.logger.info( f"Diarization successful. time to diarize: {elapsed_time(diarization_start_time, time.time())}")
        self.performance_data[CONST.DIARIZATION_TIME_KEY] = normalized_time(diarization_start_time, end_time)
        #
        speakers_start_time = time.time()
        try:
            result = assign_word_speakers(diarize_segments, aligned_segments)
            end_time = time.time()
            self.logger.info( f"Speaker assignment successful. Time to assign: {elapsed_time(speakers_start_time, end_time)}")
            self.performance_data[CONST.SPEAKER_TIME_KEY] = normalized_time(speakers_start_time, end_time)
        except Exception as e:
            STATUS.ExitStatus.whisperX_speaker_error()
            end_time = time.time()
            warn_msg = f"Error while assigning speakers: {STATUS.err_to_str(e)}"
            self.logger.warning( STATUS.statusmsg( warn_msg ) )
            result = aligned_segments

        return result

    def write_result(self, result):
        """
        Write the transcription to the specified output directory and filename.

        Args:
            result (dict): Result from transcribing the audio file.
        """
        process = 'diarization' if self.enable_diarization else 'transcription'
        status_msg_suffix = ", replacing existing file" if Path(self.output_filename).exists() else ''
        try:
            Path(self.output_dir_abspath).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            STATUS.ExitStatus.internal_error()
            err_msg = STATUS.errmsg( f"Error during {process}: {STATUS.err_to_str(e)}" )
            self.logger.error( err_msg )
            self.performance_data[CONST.OUTCOME_KEY] = err_msg
            return False
        #
        segment_error_count = 0
        segment_number = -1
        bad_segment_list = []
        with open(self.output_filename, "w", encoding="utf-8") as output_file:
            for segment in result["segments"]:
                segment_number += 1
                this_segment_error = False
                segment_start = segment_end = segment_speaker = segment_text = '?'
                if self.enable_diarization:
                    try:
                        segment_speaker = segment['speaker']
                    except Exception as e:
                        STATUS.ExitStatus.whisperX_segment_speaker_error()
                        this_segment_error = True
                try:
                    segment_start = segment['start']
                    segment_end = segment['end']
                except Exception as e:
                    STATUS.ExitStatus.whisperX_segment_timeframe_error()
                    this_segment_error = True
                try:
                    segment_text = segment['text']
                except Exception as e:
                    STATUS.ExitStatus.whisperX_segment_content_error()
                    this_segment_error = True
                if this_segment_error:
                    segment_error_count += 1
                    bad_segment_list += [segment_number]
                segment_msg = f"[{segment_start} - {segment_end}] {segment_speaker} {segment_text}\n"
                try:
                    output_file.write( segment_msg )
                except Exception as e:
                    STATUS.ExitStatus.internal_error()
                    err_msg = STATUS.errmsg( f" Error during {process}: {STATUS.err_to_str(e)}" )
                    self.logger.error( err_msg )
                    self.performance_data[CONST.OUTCOME_KEY] = err_msg
                    return False
        #
        segment_count = len(result['segments'])
        self.logger.info( f"Wrote {process} to {self.output_filename}{status_msg_suffix}" )
        self.logger.info( f"count of segments: {segment_count}" )
        self.performance_data[CONST.TOTAL_SEGMENT_COUNT_KEY] = segment_count
        self.performance_data[CONST.BAD_SEGMENT_COUNT_KEY] = segment_error_count
        self.performance_data[CONST.BAD_SEGMENT_LIST_KEY] = ','.join( [str(i) for i in bad_segment_list] )
        if segment_error_count:
            self.logger.warning( f"count of segment errors: {segment_error_count}" )
        return True
