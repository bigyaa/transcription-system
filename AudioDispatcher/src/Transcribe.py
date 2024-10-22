# *************************************************************************************************************************
#   Transcribe.py – Transcribe and diarize recordings
# *************************************************************************************************************************
#   Usage:
#       This module's Transcribe function uses the CoreAudioProcessor module to transcribe and optionally diarize
#       audio files.
# -------------------------------------------------------------------------------------------------------------------------
#   Design and Implementation Notes:
#   -.  Transcribe() uses WhisperX, a library is that is downloadable  available from at https://github.com/m-bain/
#       -.  WhisperX is a third party library that augments OpenAI's transcription library,
#           Whisper transcription service, with support for diarization.
#           -.  It features a diarization pipeline to distinguish between different speakers within the audio.
#           -.  It labels Whisper segments with speaker tags to enhance transcript readability.
#      -.  To access it, Users of WhisperX prospective users must create an account at that URL and request a key token.
# -------------------------------------------------------------------------------------------------------------------------
#   last updated: 29 June 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# constants
# ***********************************************

CONSECUTIVE_FAILURES_MAX = 5

# ***********************************************
# imports
# ***********************************************

# ==============================================================================================
#  Python standard library
# ==============================================================================================
#
# copy - structure-copying primitives
#    copy - make shallow copies of (e.g.) lists
# datetime - module for manipulating dates and times
#    datetime.now - function to get the current date and time
# pathlib - 
#    Path - file path manipulation
# subprocess - 
#    Popen - execute subordinate process
# time -
#    ctime - returns current time of day

import copy
from datetime import datetime
from pathlib import Path
import subprocess
import time
import sys


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
#     AUDIODIR_KEY              - directory with files to transcribe
#     EXTENSIONS_KEY            - Extensions to treat as audio files in the specified directory tree
#
#     ENABLE_LOGGING_KEY        - whether to write to a log file
#     USER_LOGS_DIR_KEY         - target directory for user-visible logs
#     SUMMARY_LOG_NAME_KEY      - the name/ time/ status only log
#     DETAILED_LOG_NAME_KEY     - log for capturing all output from the audio processor
#     PERFORMANCE_LOG_NAME_KEY  - log for capturing all performance data from the audio processor
#
#     PYTHON_KEY                - path to the Python interpreter
#     AUDIO_PROCESSOR_KEY       - path to the supporting single-file audio processor application
#     PROCESSOR_CONFIG_FILE_KEY - configuration file for the audio processor
#     BATCH_SIZE_KEY            - Number of audio segments to process simultaneously
#     COMPUTE_TYPE_KEY          - Type of computation (precision) to use, such as 'int8' or 'float16'
#     DEVICE_KEY                - Type of hardware device to use; either 'cpu' or 'gpu'
#     ENABLE_DIARIZATION_KEY    - specify whether to diarize as well as transcribe
#     HF_TOKEN_KEY              - Hugging Face (HF) authentication token for using models hosted on HF
#     MODEL_SIZE_KEY            - The Whisper model to use - 'tiny', 'base', 'small', 'medium', 'large'
#     OUTPUT_DIR_KEY            - directory for output from the program
#     ENABLE_OVERWRITE_KEY      - specify whether to overwrite transcription and diarization outputs, if present
#
#     TOTAL_RUN_TIME_KEY        - run time for all files in audiodir
#     MINUTES_KEY               - expressed as minutes
#     SECONDS_KEY               - with additional seconds 
#          
# XMLProcessor - manipulate XML files and content
#   openTag, closeTag, make_elt - XML tag / element generation

import src.StatusManager  as STATUS
import src.CONSTANTS      as CONST
import src.XMLProcessor   as XML

# ==============================================================================================
#   auxiliary definitions, routines
# ==============================================================================================

n_min = lambda elapsed_t: round(elapsed_t)//60
n_sec = lambda elapsed_t: round(elapsed_t)%60
normalized_time = lambda start, end: {CONST.MINUTES_KEY: n_min(end-start), CONST.SECONDS_KEY: n_sec(end-start)}

def elapsed_time_message(start_time, end_time):
    elapsed_t = end_time - start_time
    elapsed_min = '' if not n_min(elapsed_t) else f'{n_min(elapsed_t)} min'
    elapsed_sec = '' if not n_sec(elapsed_t) else f'{n_sec(elapsed_t)} sec'
    elapsed_min_sec = ', '.join( [s for s in [elapsed_min, elapsed_sec ] if s != '' ] )
    if not elapsed_min_sec:  elapsed_min_sec = '<1 sec'
    return elapsed_min_sec

final_log_border = "="*40

performance_log_open_tag =   lambda: XML.open_tag( 'multi_recording_performance_data' )
performance_log_close_tag =  lambda: XML.close_tag( 'multi_recording_performance_data' )


# ==============================================================================================
#   main routine
# ==============================================================================================

def Transcribe(config_authority, logger):
    """
    Initialize the CoreAudioProcessor with specified configuration.

    Args:
        config_authority: object with a get() method for accessing parameters.
        logger (logging.Logger): Logging object for capturing status messages.
    """
    # Set operating parameters
    #
    # --- directory tree parameters
    audiodir = config_authority.get(CONST.AUDIODIR_KEY)
    STATUS.statusmsg.filename = STATUS.errmsg.filename = audiodir
    extensions = [e.lower() for e in config_authority.get(CONST.EXTENSIONS_KEY)]
    #
    # --- executables
    python_interpreter = Path(config_authority.get(sys.executable)).absolute()
    audio_processor =    Path(config_authority.get(CONST.AUDIO_PROCESSOR_KEY)).absolute()
    #
    # --- audioDispatcher status message parameters
    model_size = config_authority.get(CONST.MODEL_SIZE_KEY)
    enable_diarization = config_authority.get(CONST.ENABLE_DIARIZATION_KEY)
    #
    # --- transcription and diarization parameters
    user_logs_dir = Path(config_authority.get(CONST.USER_LOGS_DIR_KEY)).absolute()
    #
    subprocess_log_file_name = datetime.now().strftime('coreProcessorInternalTracking_%Y_%m_%d_%H_%M_%S.log')
    subprocess_log_file_path = Path(user_logs_dir, subprocess_log_file_name)
    subprocess_log_file_path.unlink(missing_ok=True)
    subprocess_log_file = str(subprocess_log_file_path)
    #
    subprocess_data_log_file_name = datetime.now().strftime('coreProcessorInternalDataTracking_%Y_%m_%d_%H_%M_%S_log.xml')
    subprocess_data_log_file_path = Path(user_logs_dir, subprocess_data_log_file_name)
    subprocess_data_log_file_path.unlink(missing_ok=True)
    subprocess_data_log_file = str(subprocess_log_file_path)
    #
    audio_processor_params = {
        "-cx": config_authority.get(CONST.PROCESSOR_CONFIG_FILE_KEY),
        "-bs": config_authority.get(CONST.BATCH_SIZE_KEY),
        "-ct": config_authority.get(CONST.COMPUTE_TYPE_KEY),
        "-dv": config_authority.get(CONST.DEVICE_KEY),
        "-ed": enable_diarization,
        "-el": True,
        "-ht": config_authority.get(CONST.HF_TOKEN_KEY),
        "-ld": user_logs_dir,
        "-ln": subprocess_log_file_name,
        "-lp": subprocess_data_log_file_path,
        "-ms": model_size,
        "-ov": config_authority.get(CONST.ENABLE_OVERWRITE_KEY)
    }
    #
    subprocess_parameters  = [python_interpreter, audio_processor]
    subprocess_parameters += [f"{key}={value}" for key, value in audio_processor_params.items() if value is not None]
    #
    if (enable_logging := config_authority.get(CONST.ENABLE_LOGGING_KEY)):
        summary_log_file_path = Path(user_logs_dir, config_authority.get(CONST.SUMMARY_LOG_NAME_KEY))
        summary_log_file_path.unlink(missing_ok=True)
        summary_log_file  = str(summary_log_file_path)
        #
        detailed_log_file_path = Path(user_logs_dir, config_authority.get(CONST.DETAILED_LOG_NAME_KEY))
        detailed_log_file_path.unlink(missing_ok=True)
        detailed_log_file  = str(detailed_log_file_path)
        #
        performance_log_file_path = Path(user_logs_dir, config_authority.get(CONST.PERFORMANCE_LOG_NAME_KEY))
        performance_log_file_path.unlink(missing_ok=True)
        performance_log_file = str(performance_log_file_path)
        with open(performance_log_file, "w") as output_file:
            output_file.write( XML.xml_declaration +'\n' )
            output_file.write( performance_log_open_tag() +'\n' )

    logger.info(f"Transcribing with {'default' if model_size is None else model_size} model")

    dispatcher_start_time = time.time()

    output_dir = config_authority.get(CONST.OUTPUT_DIR_KEY)
    audiodir_path_len = len(Path(Path(audiodir).absolute()).parts)
    consecutive_failure_counter = 0
    
    def write_supplemental_logs( message, eol="\n" ):
        with open(summary_log_file, "a") as output_file:
            output_file.write( message+eol )
        with open(detailed_log_file, "a") as output_file:
            output_file.write( message+eol )

    for (dirpath, _, filenames) in Path(audiodir).walk():
        for audio in [file for file in filenames if Path(file).suffix.lower() in extensions]:
            audio_path_absolute = Path(dirpath, audio).absolute()
            #
            dirpath_path_obj = Path(dirpath)
            dirpath_path_abspath_obj = Path(dirpath_path_obj.absolute())
            dirpath_len = len(dirpath_path_abspath_obj.parts)
            dirpath_suffix = [ dirpath_path_abspath_obj.parts[i] for i in range(audiodir_path_len, dirpath_len) ]
            this_output_dir = Path(Path(output_dir).joinpath( *dirpath_suffix )).absolute()
            #
            this_subprocess_parameters = copy.copy( subprocess_parameters )
            this_subprocess_parameters += [ f"-au={audio_path_absolute}" ]
            this_subprocess_parameters += [ f"-od={this_output_dir}" ]
            #
            info_message = f"Transcribe: processing {audio_path_absolute}"
            write_supplemental_logs( info_message )
            logger.info( info_message )
            #
            err_msg, err_msg_plus = None, None
            syndrome_type = None
            try:
                processor_start_time = time.time()
                process = subprocess.Popen(
                            this_subprocess_parameters,
                            cwd=Path(audio_processor).parent,
                            encoding='utf8',
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE
                )
                stdout_text, stderr_text = process.communicate()
                exit_code = process.wait()
                processor_end_time = time.time()
                if stdout_text:  
                    print( stdout_text )
                    logger.info( f"stdout content: ({stdout_text})" )
                if stderr_text:  
                    print( stderr_text )
                    logger.info( f"stderr content: ({stderr_text})" )
                #
                syndrome_type = None if exit_code == 0 else ( 'Warn' if exit_code == 1 else 'Error' )
                consecutive_failure_count = 0 if exit_code <= 1 else consecutive_failure_count+1
                if exit_code:
                    with open(subprocess_log_file, "r") as input_file:
                        detailed_log_content = input_file.read()+'\n'
                    if detailed_log_content:
                        logger.info( 'core audio processor log:\n' + detailed_log_content )
            except FileNotFoundError as e:
                err_msg = 'Transcribe: cannot find one more more required files'
                err_msg_plus = '\npossible files:\n'
                err_msg_plus += f'Python interpreter:   {python_interpreter}\n'
                err_msg_plus += f'Core audio processor: {audio_processor}\n'
                err_msg_plus += f'Recording to process: {audio_path_absolute}'
                exit_code = STATUS.ExitStatus.missing_file()
                syndrome_type = 'Fatal'
            except Exception as e:
                err_msg = f"Exception occurred during processing: {e}\n"
                exit_code = STATUS.ExitStatus.uncertain_error()
                syndrome_type = 'Error'
            #
            e_t = elapsed_time_message( processor_start_time, processor_end_time )
            write_supplemental_logs( f'Transcribe: processing time: {e_t}' )
            write_supplemental_logs( f'Transcribe: exit code: {exit_code}' )
            if syndrome_type:
                if err_msg:
                    write_supplemental_logs( err_msg )
                    logger.info( err_msg )
                    if err_msg_plus:
                        with open(detailed_log_file, "a") as output_file:
                            output_file.write( err_msg_plus )
                        logger.info( err_msg_plus )
                with open(detailed_log_file, "a") as output_file:
                    if stdout_text:
                        output_file.write( f"stdout content: ({stdout_text})" )
                    if stderr_text:  
                        output_file.write( f"stderr content: ({stderr_text})" )
                if syndrome_type == 'Fatal' or syndrome_type == 'Error':
                    subprocess_log_file_path.unlink(missing_ok=True)
                    subprocess_data_log_file_path.unlink(missing_ok=True)
                    with open(detailed_log_file, "a") as output_file:
                        output_file.write( f'process parameters: {this_subprocess_parameters}\n' )
                    if syndrome_type == 'Error':
                        consecutive_failure_counter += 1
                        if consecutive_failure_counter > CONSECUTIVE_FAILURES_MAX:
                            write_supplemental_logs( f"Exceeded maximum failure limit ({CONSECUTIVE_FAILURES_MAX}). Exiting." )
                            syndrome_type = 'Fatal'
                    write_supplemental_logs( final_log_border )
                    if syndrome_type == 'Fatal':
                        logger.critical( 'Transcribe: fatal error detected - exiting' )
                        break
                    logger.warning( 'Transcribe: processing of current file failed - continuing' )
                    continue
                logger.warning( 'Transcribe: processing of current file completed, but with errors' )
            #
            write_supplemental_logs( final_log_border )
            if enable_logging:
                with open(performance_log_file, "a") as output_file, open(subprocess_data_log_file_path, "r") as input_file:
                    input_file.readline()       # clear the xml declaration
                    for line in input_file:   
                        output_file.write( line )
                    output_file.write( '\n' )
            subprocess_log_file_path.unlink(missing_ok=True)
            subprocess_data_log_file_path.unlink(missing_ok=True)
    #
    # announce shutdown, fill out the summary log
    end_time = time.time()
    final_message = f"Total elapsed time: {elapsed_time_message(dispatcher_start_time, end_time)}"
    logger.info( final_message )
    write_supplemental_logs( final_message )
    #
    # finish compiling the performance log, then pretty print its contents
    if enable_logging:
        with open(performance_log_file, "a") as output_file:
            # False => avoid prettyprinting the XML content - and throwing in an XML declaration at this point in the output
            output_file.write( XML.asXML( CONST.TOTAL_RUN_TIME_KEY, normalized_time(dispatcher_start_time, end_time), logger, False ) )
            output_file.write( performance_log_close_tag() )
        with open(performance_log_file, "r") as input_file:
            performance_file_content = ''
            for line in input_file:
                performance_file_content += line
        with open(performance_log_file, "w") as output_file:
            for line in XML.prettyPrint( performance_file_content ):
                output_file.write( line )
            

