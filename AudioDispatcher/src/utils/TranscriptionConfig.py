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

# config.DEFAULTS - module to handle default configuration settings for the transcription system
#   DEFAULT_* - constants defining default values for configuration settings
# lxml.etree - provides XML parsing and validation functionality
#   parse - function to parse an XML document into an element tree
#   XMLSchema - class to validate an XML document against XML Schema
# os – operating system primitives
#   path.isfile – test if argument is a file:
# src.utils - custom package for utility functions related to the transcription model
#   helperFunctions - module with functions for command-line argument parsing and XML file validation

import os
import sys
import xml.etree.ElementTree as ET
import xmlschema

from config.DEFAULTS import (DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_FILE_SCHEMA,
                             DEFAULT_WHISPER_CONFIG)
from src.utils.helperFunctions import (format_error_message, logger,
                                       parse_command_line_args,
                                       validate_configxml)
from src.utils.applicationStatusManagement import ExitStatus, FileFormatError, ConfigurationError
import src.utils.applicationStatusManagement as STATUS

# ******************************************************************************************************
#  auxiliary classes and functions
# ******************************************************************************************************

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# config file parsing
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =======================================================================================================
# helper function for argparse
# =======================================================================================================

# =====================================================================================================================
# XMLConfigFile - access a flat (depth 2) XML configuration file's contents
# ---------------------------------------------------------------------------------------------------------------------
# XML config file expected format:
#    logfile - a string naming a file for logging
#    output_dir - a string naming a directory in which to store output files
#    manifest_file - a string naming a file for recording the names of files that this application creates
# all elements are optional
#
# XMLConfigFile has two major methods
# -.  __init__ - loads specified file, validating it against specified schema
# -.  contents - returns a quadruple
#       first value is a dict that presents the file's contents
#       second value holds a nonempty error message if the config file couldn't be accessed
#       third value holds a nonempty error message if the schema file couldn't be accessed
#       fourth value holds a nonempty error message if the config file's contents couldn't be successfully validated
# =====================================================================================================================


class XMLConfigFile(object):
    def __init__(self, config_file=DEFAULT_CONFIG_FILE, config_schema=DEFAULT_CONFIG_FILE_SCHEMA):
        #
        self._contents = {}
        self.file_missing = []
        self.file_malformed = []
        self.schema_missing = []
        self.schema_malformed = []
        self.file_invalid = []
        #
        # step 1 - retrieve file's contents as a dictionary
        #
        if not os.path.isfile(config_file):
            self.file_missing = [
                f"XMLConfigFile: config file {config_file} not found"]
        if not os.path.isfile(config_schema):
            self.schema_missing = [
                f"XMLConfigFile: config schema {config_schema} not found"]
        #
        if self.file_missing:
            return
        #
        try:
            parsed_config_file = ET.parse(config_file)
        except ET.ParseError as e:
            self.file_malformed = [
                f"XMLConfigFile: cannot parse {config_file} - {STATUS.err_to_str(e)}"]
            return
        #
        self._contents = dict([(e.tag, e.text)
                              for e in parsed_config_file.iterfind("./*")])
        #
        # step 2 - validate the file
        #
        if self.schema_missing:
            return
        #
        try:
            parsed_config_file_schema = xmlschema.XMLSchema(config_schema)
        except Exception as e:
            self.schema_malformed = [
                f"XMLConfigFile: invalid schema {config_schema} - {STATUS.err_to_str(e)}"]
            return
        #
        try:
            parsed_config_file_schema.validate(config_file)
        except Exception as e:
            self.file_invalid = [
                f"XMLConfigFile: schema {config_schema} won't validate {config_file} - {STATUS.err_to_str(e)}"]

    def contents(self):
        return (self._contents, self.file_missing, self.file_malformed, self.schema_missing, self.schema_malformed, self.file_invalid)


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
        parsed_xml_file = XMLConfigFile(config_file)

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
                  return default
              else:
                  logger.error(f'Could not find element in configuration file: {key}')
                  STATUS.ExitStatus.internal_error()
      except Exception as e:
          logger.error(f'Error accessing configuration file: {format_error_message(e)}')
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
