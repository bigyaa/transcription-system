# *************************************************************************************************************************
#   SegmentMerger.py – Combine adjacent segments from a common speaker in a WhisperX transcript
# *************************************************************************************************************************
#   About:
#      This module contains MergeSegments(), a function that reformats input from a WhisperX transcript,
#      combining adjacent segments from a common speaker into a single paragraph, 
#      prefaced by a single speaker name and time range.
#   Parameters:
# -------------------------------------------------------------------------------------------------------------------------
#   Design and Implementation Notes:
#   -.  The input is to be formatted as a sequence of lines, each of which 
#       -.  begins with a label of the form  [ start_time - end_time ] SPEAKER_nn
#           where the start and end times are decimal values and nn is a two-digit number
#       -.  ends with a string of text 
# -------------------------------------------------------------------------------------------------------------------------
#   last updated: 18 May 2024
#   authors:  Bigya Bajarcharya, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# constants
# ***********************************************

MAX_ERRORS = 10

# ***********************************************
# imports
# ***********************************************

# ======================================================================================
#   Python Standard Library
# ======================================================================================
#
# re -
#    match - check a string for conformance to a pattern
# sys –
#   exit – exit, returning a final status code
#
import re
import sys

# ======================================================================================
#   custom
# ======================================================================================
#
# StatusManager - supporting definitions for error management

import src.StatusManager as STATUS


# ***************************************************************************************************************************
#  main function
# ***************************************************************************************************************************

#************************************************
# Main module function
#
# MergeSegments - 
#   Merge segments from a WhisperX output, collapsing adjacent segments from a common speaker
#   into a single paragraph and updating the overall time frame
#
# Input:    
#      transcript:          The file to update
#      updated_transcript:  The name of a file to capture the revised content
#      logger:              The name of a file for capturing error message
#           infile:  The input text containing dialogues with timestamps and speaker labels.
# Output:   A list of dictionaries, each containing merged dialogue information with
#           speaker, dialogue, start_time, and end_time.
#
#************************************************

# Function to return collapsed segment information as a dict
def update_segment_list(segment_list, start, end, speaker, dlog)
  if speaker is None: return
  segment_list +=  [ {'speaker': speaker, 'start_time': start, 'end_time': end, 'dialogue': dlog.strip()} ]

def MergeSegments(transcript, updated_transcript, logger):
  
  # Load the text from the file
  try:
    with open(transcript, 'r', encoding='ISO-8859-1') as file:
      text = file.read()
  except FileNotFoundError as e:
    err_msg = f"Missing file -{transcript}: {e}\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.missing_file() )
  except IOError as e:
    err_msg = f"I/O error occurred while processing {transcript}: {e}\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.file_access_error() )
  except Exception as e:
    err_msg = f"Exception occurred while processing {transcript}: {e}\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.uncertain_error() )

  # Split text into lines, dropping any blank lines at end of text 
  lines = text.split('\n')
  while lines and not lines[-1]:
    lines = lines[:-1]
  if not lines:
    err_msg = f"Format error in {transcript}: file is devoid of text\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.file_format_error() )
  
  # Process text
  merged_segments = []
  this_speaker = None
  
  error_count = 0
  for (lineno, this_line) in enumerate(lines):
 
    # Extract speaker, start_time, end_time, and dialogue using regular expression
    match = re.match(r'\[(\d+\.\d+) - (\d+\.\d+)\] (SPEAKER_\d+) (.*)', this_line) )
    
    if not match:
      error_count += 1
      err_msg = f"Format error in {transcript} at line {lineno}: improper format ({this_line})\n"
      if error_count > MAX_ERRORS:
        err_msg += f"Error threshhold exceeded: exiting\n"
        logger.critical( err_msg )
        sys.exit( STATUS.ExitStatus.file_format_error() )
      logger.error( err_msg )
      STATUS.ExitStatus.transcript_format_irregularity()
      update_segment_list( merged_segments, this_start_time, this_end_time, this_speaker, this_dialogue )
      this_speaker = None
      continue
    
    next_speaker = match.group(3)
    if this_speaker == next_speaker:
      this_dialogue += ' ' + match.group(4) 
      continue

    update_segment_list( merged_segments, this_start_time, this_end_time, this_speaker, this_dialogue )
    this_dialogue = match.group(4)      
    this_speaker = next_speaker
    this_start_time = match.group(1)
    this_end_time = match.group(2)

  update_segment_list( merged_segments, this_start_time, this_end_time, this_speaker, this_dialogue )

  # Sort dialogues based on start_time
  # print(merged_segments)
  # merged_segments = sorted(merged_segments, key=lambda item: float(item['start_time']))
  
  # Output sorted content to target file, if not present
  try:
    with open(updated_transcript, 'x', encoding='ISO-8859-1') as f:
      for segment in merged_segments:
        print(f"[{segment['start_time']} - {segment['end_time']}] {segment['speaker']}: {segment['dialogue']}\n", file=f)
  except IOError as e:
    err_msg = f"I/O error occurred while outputting {transcript}: {e}\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.file_access_error() )
  except Exception as e:
    err_msg = f"Exception occurred while processing {transcript}: {e}\n"
    logger.critical( err_msg )
    sys.exit( STATUS.ExitStatus.uncertain_error() )
  