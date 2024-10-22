# *************************************************************************************************************************
#   main.py 
#     Entry point for the WhisperX-based audio transcription application. 
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#      python main.py --audio [path_to_audio_file] --configxml [path_to_config_file] [Other_Arguments]
#      Arguments and defaults:
#         -au, --audio_file [path]: Path to the audio file for transcription
#         -bs, --batch_size [size]:  Batch size for transcription
#         -cx, --configxml [path]: XML configuration file.
#         -ct, --compute_type: The computation type
#         -dv, --device: hardware device for diarization.  Defaults to 'cpu'
#         -ht, --hf_token [token]: Hugging Face token for model access with diarization.
#         -ed, --enable_diarization: If true, diarize after transcription
#         -ld, --logfile_dir [path] : Name of directory into which to write logfile.
#         -ln, --logfile_name [path]: Name of log file to write.
#         -lp, --performance_log_name [path]: Name of log file for capturing performance data.
#         -ms, --model_size [size]: Whisper model size for transcription.
#         -od, --output_dir [dir]: Directory to store transcription files.
#         -ov, --overwrite: If True (default), overwrite existing transcription and diarization, if present.
#         -el, --enable-logfile: If True (default), write log messages to log file, as well as console.
#      Outputs:
#         Processes and transcribes audio files, outputting transcription files in the specified directory.
#         IF enabled,
#            application activity and errors are logged.
#            final performance data is logged.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated:  16 May, 2024
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
# CONSTANTS - values for cross-module constants
#   STATUS_KEY - final status code
#   OUTCOME_KEY - natural language characterization of overall process outcome
#   TRANSCRIPTION_TIME_KEY - time to transcribe input
#   DIARIZATION_TIME_KEY - time to diarize input
#   TOTAL_TIME_KEY - total time for execution
#   TOTAL_SEGMENT_COUNT_KEY - count of segments
#   BAD_SEGMENT_COUNT_KEY - count of bad segments
# XMLProcessor - XML manipulation
#   asXML - transform a dict's contents into an XML-formatted dataset
# TranscriptionConfig - configuration handler for transcription settings
#   TranscriptionConfig - class to manage transcription configuration from an XML file
# WhisperxTranscriber - package for the transcription model
#   WhisperxTranscriber - class to handle transcription process using Whisper models

import src.StatusManager as STATUS
import src.CONSTANTS as CONST
import src.XMLProcessor as XML
from src.TranscriptionConfig import TranscriptionConfig
from src.WhisperxTranscriber import WhisperxTranscriber

# ***********************************************
# program main
# ***********************************************

if __name__ == '__main__':
    # Configure program execution.
    config = TranscriptionConfig()
    logger = config.logger()    
    try:
        model = WhisperxTranscriber(config, logger)
        summary_data = model.transcribe()
        status_msg = STATUS.statusmsg( ' Processing completed.' )
        logger.info( status_msg )
    except Exception as e:
        summary_data = CONST.null_transcription_data()
        err_msg = STATUS.errmsg( f'?? exiting: {STATUS.err_to_str(e)}' )
        logger.error( err_msg )
    exit_status = STATUS.ExitStatus.status
    if ( performance_log := config.performance_log_name() ) is not None:
        summary_data[CONST.STATUS_KEY] = exit_status
        with open(performance_log, 'w') as fp:
            fp.write( XML.asXML( 'performance_data', summary_data, logger ) )
    sys.exit( exit_status )

