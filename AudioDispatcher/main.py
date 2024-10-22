# *************************************************************************************************************************
#   main.py
#     Entry point for the WhisperX-based audio transcription application.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio_path [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#      Arguments and defaults:
#
#         -au,   --audiodir [path]:              Path to the directory tree containing files to transcribe  [required]
#         -cxds, --config_dispatcher [path]:     XML configuration file for the dispatcher.
#         -ex,   --extensions:                   List of file extensions to treat as recordings
#
#         -el,   --enable_logging:                    If True, write log messages to log file, as well as console.
#         -ld,   --logfile_dir [path]:                Directory for storing user-visible dispatcher log files. 
#                                                       special names:
#                                                         stdout - denotes standard output channel
#                                                         stderr - denotes standard error channel
#                                                         null - denotes the null device
#         -lnsm,  --summary_logfile_name [path]:      Name of dispatcher summary log file
#         -lndt,  --detailed_logfile_name [path]:     Name of detailed version of log file
#         -lnpf,  --performance_logfile_name [path]:  Name of performance data log file
#
#         -py,   --python:                   Python interpreter.  Defaults to /usr/local/bin/python
#         -pr,   --audio_processor:          Single-file transcriber and diarizer.  Defaults to CoreAudioProcessor/main.py.
#         -cxpr, --config_processor [path]:  XML configuration file for the transcriber.
#
#         parameters that apply to all files to process in audiodir:
#         -bs,   --batch_size [size]:        Batch size for transcription
#         -ct,   --compute_type:             The computation type
#         -dv,   --device:                   hardware device for diarization - 'cpu' or 'gpgpu'
#         -ed,   --enable_diarization:       If True, enable diarization as well as transcription
#         -ht,   --hf_token [token]:         Hugging Face token for model access with diarization.
#         -ms,   --model_size [size]:        Whisper model size for transcription. 
#         -od,   --output_dir [dir]:         Directory for storing transcription file outputs.
#         -ov,   --enable_overwrite:         If True, overwrite existing transcription and diarization, if present.
#
#      Outputs:
#         Processes and transcribes audio files, outputting transcription files in the specified directory.
#         Application activity and errors are logged.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  May 16 2024
#   authors:       Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# --------------------------------------------------------------------------------------
#   Python Standard Library
# --------------------------------------------------------------------------------------
#
# sys –
#   exit – exit, returning a final status code

import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# StatusManager - supporting definitions for error management
# TranscriptionConfig - configuration handler for transcription settings
#   TranscriptionConfig - class to manage transcription configuration from an XML file
# Transcribe - package for the transcription model
#   Transcribe - class to handle transcription process using CoreAudioProcessor module

import src.StatusManager as STATUS
from src.TranscriptionConfig import TranscriptionConfig
from src.Transcribe import Transcribe

# ***********************************************
# program main
# ***********************************************

if __name__ == '__main__':

    # Configure program execution.
    config = TranscriptionConfig()
    logger = config.logger()

    # Transcribe the input
    try:
        Transcribe(config, logger)
        status_msg = STATUS.statusmsg(': Processing completed.')
        logger.info(status_msg)
        sys.exit(STATUS.ExitStatus.status)
    except Exception as e:
        err_msg = STATUS.errmsg(f' ?? exiting: {STATUS.err_to_str(e)}')
        logger.error(err_msg)
        sys.exit(STATUS.ExitStatus.uncertain_error())
