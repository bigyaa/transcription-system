# *************************************************************************************************************************
#   XMLProcessor.py
#       Supporting logic for processing XML content, including schema validation
# -------------------------------------------------------------------------------------------------------------------------
#   Usage:
#      The module's codes support access to and creation of XML files and content
# -------------------------------------------------------------------------------------------------------------------------
#   Design Notes:
#   -.  This module was tested using Python 3.12.  It hasn't been tested with earlier versions of Python.
# --------------------------------------------------------------------------------------------------------------------------
#   last updated:  12 February 2024
#   author: Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ---------------------------------------------------------------------------------------------------------------------
#   python standard library
# ---------------------------------------------------------------------------------------------------------------------

# os.path – operating system primitives
#    abspath - return the full path name for the given argument
#    exists - test is argument exists in the file system
#    isdir - test if argument is a directory
#    isfile – test if argument is a file
# xml.dom.minidom -
#    parsestring - parses a string representation of an XML file
#    topretty - pretty-prints a parsed XML string
# xml.etree - provides XML parsing and validation functionality
#    parse - function to parse an XML document into an element tree
#    XMLSchema - class to validate an XML document against XML Schema
#
import os
import xml
from xml.dom import minidom as MINIDOM
from xml.etree import ElementTree as ET

import config.DEFAULTS as DEFAULT
import src.utils.applicationStatusManagement as STATUS

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# applicationStatusManagement - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
# config.DEFAULTS - supporting definitions for forms parsing
#   DEFAULT_CONFIG_FILE -              XML file for overriding selected default values
#   DEFAULT_CONFIG_FILE_SCHEMA -       XML file for validating configuration files


# ---------------------------------------------------------------------------------------------------------------------
#   PyPi (i.e. pip) repository
# ---------------------------------------------------------------------------------------------------------------------

# xmlschema - xml schema support
#    parse - use specified grammar to parse specified content
#    XMLschema - validate specified schema

try:
  import xmlschema
except:
  err_msg = f"\nPyPi's xmlschema library not yet installed - execute pip install xmlschema, then rerun this program"
  error_message = STATUS.errmsg(err_msg)
  STATUS.ExitStatus.improper_environmental_configuration()
  raise STATUS.ConfigurationError(err_msg)

# ***********************************************
# main modules
# ***********************************************

# ==========================================================================================================================
# Function for generating XML for output
# Parameters:
# -.  name of top-level element for XML tree
# -.  contents, as possibly recursive list of dictionaries or (key, value) pairs
# -.  logger - for generating error messages
# ==========================================================================================================================

make_elt = lambda key, value: (
    f"<{str(key).lower()}/>"
    if value is None
    else f"<{str(key).lower()}>{str(value).strip(' ')}</{str(key).lower()}>"
)


def asXML(outer_tag, content, logger):
    def asXMLcontent(stuff):
        if isinstance(stuff, dict):
            return asXMLcontent(list(stuff.items()))
        if (len(stuff) == 2) and isinstance(stuff[0], (str, int)):
            if isinstance(stuff[1], (str, int, type(None))):
                return make_elt(
                    stuff[0],
                    (
                        None
                        if stuff[1] is None
                        else str(stuff[1]).replace("&", "&amp;").replace("<", "&lt;")
                    ),
                )
            return make_elt(stuff[0], asXMLcontent(stuff[1]))
        if isinstance(stuff, list):
            return "".join([asXMLcontent(item) for item in stuff])
        err_msg = f"asXML: malformed (key, value) structure ({content}) - exiting\n"
        err_msg += f"asXML: problem subexpression - {stuff}\n"
        error_message = STATUS.errmsg(err_msg)
        logger.error(error_message)
        STATUS.ExitStatus.internal_error()
        raise STATUS.InternalError(error_message)

    contentAsXML = make_elt(outer_tag, asXMLcontent(content))
    dom = MINIDOM.parseString(contentAsXML)
    pretty_xml = dom.toprettyxml(indent="  ")
    pretty_xml = "\n".join(line for line in pretty_xml.split("\n") if line.strip())
    return pretty_xml


# =====================================================================================================================
# XMLFile - access a flat (depth 2) XML configuration file's contents
# ---------------------------------------------------------------------------------------------------------------------
#
# XMLFileFile has two major methods
# -.  __init__ - loads specified file, validating it against specified schema
# -.  contents - returns a sextuple
#       first value is a dict that presents the file's contents
#       second value holds a nonempty error message if the XML file couldn't be accessed
#       third value holds a nonempty error message if the XML file was malformed
#       fourth value holds a nonempty error message if the schema couldn't be accessed
#       fifth value holds a nonempty error message if the schema was malformed
#       sixth value holds a nonempty error message if the config file's contents couldn't be successfully validated
# =====================================================================================================================


class XMLFile(object):
    def __init__(
        self,
        config_file=DEFAULT.DEFAULT_CONFIG_FILE,
        config_schema=DEFAULT.DEFAULT_CONFIG_FILE_SCHEMA,
    ):
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
          self.file_missing = [ f"XMLConfigFile: config file {config_file} not found" ]
        if not os.path.isfile(config_schema):
            self.schema_missing = [
                f"XMLConfigFile: config schema {config_schema} not found"
            ]
        #
        if self.file_missing:
            return
        #
        try:
            parsed_config_file = ET.parse(config_file)
        except xml.etree.ElementTree.ParseError as e:
            self.file_malformed = [
                f"XMLConfigFile: cannot parse {config_file} - {STATUS.err_to_str(e)}"
            ]
            return
        #
        self._contents = dict(
            [(e.tag, e.text) for e in parsed_config_file.iterfind("./*")]
        )
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
                f"XMLConfigFile: invalid schema {config_schema} - {STATUS.err_to_str(e)}"
            ]
            return
        #
        try:
            parsed_config_file_schema.validate(config_file)
        except Exception as e:
            self.file_invalid = [
                f"XMLConfigFile: schema {config_schema} won't validate {config_file} - {STATUS.err_to_str(e)}"
            ]

    def contents(self):
        return (
            self._contents,
            self.file_missing,
            self.file_malformed,
            self.schema_missing,
            self.schema_malformed,
            self.file_invalid,
        )
