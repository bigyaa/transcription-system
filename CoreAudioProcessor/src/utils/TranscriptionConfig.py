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

from src.utils.applicationStatusManagement import ExitStatus, FileFormatError, ConfigurationError
import src.utils.applicationStatusManagement as STATUS
from config.DEFAULTS import (DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_FILE_SCHEMA,
                             DEFAULT_WHISPER_CONFIG)
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

        # if os.path.isfile(config_file):
        #     with open(config_file, 'rb') as file:
        #         self.root = ET.parse(file).getroot()
        # else:
        #     err_msg = f"Config file not found: {config_file}"
        #     logger.error(err_msg)
        #     if hasattr(self.command_line_args, 'configxml'):
        #         raise ConfigurationError(ExitStatus.missing_file())

        # if hasattr(self, 'root'):
        #     try:
        #         validate_configxml(logger, config_file, DEFAULT_CONFIG_FILE_SCHEMA)
        #         self.config_data.update({child.tag: child.text for child in self.root})
        #     except Exception as e:
        #         logger.error(f"Error loading config file: {config_file} - {format_error_message(e)}")
        #         raise ConfigurationError(ExitStatus.file_format_error())

        # for key, value in self.command_line_args.items():
        #     if value is not None:
        #         self.config_data[key] = value

        # print(f"Config data: {self.config_data}")
        (config_data, file_missing, file_malformed, schema_missing,
         schema_malformed, file_invalid) = parsed_xml_file.contents()

        setattr(self, 'config_data', config_data)

        fatal_errors = '\n'.join((file_missing if config_file else [
        ]) + file_malformed + schema_malformed + file_invalid)
        if fatal_errors:
            print(STATUS.app_errmsg("ConfigManager: " +
                  fatal_errors), file=sys.stderr)
            sys.exit(STATUS.ExitStatus.missing_file())

        warnings = '\n'.join(file_missing + schema_missing)
        if warnings:
            print(STATUS.app_infomsg(warnings), file=sys.stderr)
            STATUS.ExitStatus.missing_default_file()

    def get(self, key, default=None):
        """
        Get the value for the specified key in the configuration file.
        """
        try:
            if key in self.config_data:
                return self.config_data[key]
            else:
                if default is not None:
                    logger.info(f'Using default values for {key}')
                    return default
                else:
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
