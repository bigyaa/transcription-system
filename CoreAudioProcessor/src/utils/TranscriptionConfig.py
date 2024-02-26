# *************************************************************************************************************************
#   TranscriptionConfig.py
#       Manage the configuration for an audio transcription system, including access to XML configuration files.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The module provides an interface for interacting with the transcription configuration through the
#       TranscriptionConfig class. Functions are also available for parsing command-line arguments and for
#       validating XML configuration files.
#
#       Parameters:
#           Various parameters can be defined in an XML configuration file, which are then parsed and applied to
#           the transcription system. Command-line arguments can override configuration file settings.
#
#       Outputs:
#           The TranscriptionConfig class provides methods to retrieve and set configuration values, and to
#           create or delete configuration keys.
#
#   Design Notes:
#   -.  The module uses lxml for XML parsing and validation.
#   -.  Custom utility functions are used for command-line parsing and XML validation.
#   -.  The logging module provides feedback and error reporting.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated: January 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede, Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# lxml.etree - provides XML parsing and validation functionality
#   parse - function to parse an XML document into an element tree
#   XMLSchema - class to validate an XML document against XML Schema

import sys

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# applicationStatusManagement - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     transcript_errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
# DEFAULTS - supporting definitions for forms parsing
#   DEFAULT_CONFIG_FILE -              XML file for overriding selected default values
#   DEFAULT_CONFIG_FILE_SCHEMA -       XML file for validating configuration files
# src.utils - custom package for utility functions related to the transcription model
#   helperFunctions - module with functions for command-line argument parsing and XML file validation
# XMLProcessor - manipulate XML files and content
#   XMLFile - parse and validate XML files

import src.utils.applicationStatusManagement as STATUS
from config.DEFAULTS import (DEFAULT_CONFIG_FILE)
from src.utils.helperFunctions import (format_error_message, logger,
                                       parse_command_line_args)
import src.utils.XMLProcessor as XML

# ******************************************************************************************************
#  auxiliary classes and functions
# ******************************************************************************************************

# =======================================================================================================
# helper function for argparse
# =======================================================================================================

# ***********************************************
#  main module
# ***********************************************


# **************************************************************************
# read XML configuration files for the transcription system.
# **************************************************************************

# TODO: separate check of config file in a separate class and use a get on config file evaluation to further processing of config file values.
class TranscriptionConfig():
    def __init__(self):
        self.command_line_args = parse_command_line_args()

        self._contents = {}

        config_file = getattr(self.command_line_args,
                              'configxml', DEFAULT_CONFIG_FILE)
        parsed_xml_file = XML.XMLFile(config_file)

        (self.config_data, file_missing, file_malformed, schema_missing,
         schema_malformed, file_invalid) = parsed_xml_file.contents()

        fatal_errors = '\n'.join((file_missing if config_file else [
        ]) + file_malformed + schema_malformed + file_invalid)
        if fatal_errors:
            print(STATUS.errmsg("TranscriptionConfig: " +
                  fatal_errors), file=sys.stderr)
            sys.exit(STATUS.ExitStatus.missing_file())

        warnings = '\n'.join(file_missing + schema_missing)
        if warnings:
            print(STATUS.errmsg(warnings), file=sys.stderr)
            STATUS.ExitStatus.missing_default_file()

    def get(self, key, default=None):
        """
        Get the value for the specified key in the configuration file.
        """
        try:
            if key in self.command_line_args and self.command_line_args[key] is not None:
                return self.command_line_args[key]
            elif key in self.config_data:
                return self.config_data[key]
            elif default is not None:
                return default
            logger.error(
                    f'Could not find element in configuration file: {key}')
            STATUS.ExitStatus.internal_error()
        except Exception as e:
            logger.error(
                f'Error accessing configuration file: {format_error_message(e)}')
            STATUS.ExitStatus.internal_error()

    def set_param(self, key, value):
        """
        Set the value for the specified key in the configuration file.

        :param key: The name of the key in the format 'parent/child' or 'key' if it has no parent.
        :param value: The new value to assign to the key.
        :return: True if the key's value was successfully updated, False otherwise.
        """
        try:
            # parts = key.split("/")
            # parent = self.root if len(
            #     parts) == 1 else self.root.find('/'.join(parts[:-1]))
            # element = parent.find(parts[-1]) if parent is not None else None

            # if element is None:
            #     element = ET.Element(parts[-1])
            #     parent.append(element)

            # element.text = value
            # logger.info(f'Set value of key "{key}" to: {value}')
            # return True
            setattr(self, key, value)
        except Exception as e:
            logger.error(
                f'Error while setting element value: {format_error_message(e)}')
            STATUS.ExitStatus.internal_error()

    def get_all(self):
        """
        Get all key-value pairs in the configuration file.
        """
        try:
            return self.contents()
        except Exception as e:
            logger.error(
                f'Error while getting all key-value pairs in configuration file: {format_error_message(e)}')
            STATUS.ExitStatus.internal_error()
