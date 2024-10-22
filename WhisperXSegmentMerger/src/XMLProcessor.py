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
#   last updated:  18 May 2024
#   author:        Phil Pfeiffer
# *************************************************************************************************************************

# ***********************************************
# imports
# ***********************************************

# ---------------------------------------------------------------------------------------------------------------------
#   python standard library
# ---------------------------------------------------------------------------------------------------------------------
#
# pathlib - 
#    Path - path manipulation primitives
# sys –
#    exit – exit, returning a final status code
#    stderr – the standard error message stream
# xml.dom.minidom -
#    parsestring - parses a string representation of an XML file
#    topretty - pretty-prints a parsed XML string
# xml.etree - provides XML parsing and validation functionality
#    parse - function to parse an XML document into an element tree
#    XMLSchema - class to validate an XML document against XML Schema
#
from pathlib import Path
import sys
import xml
from xml.dom import minidom as MINIDOM
from xml.etree import ElementTree as ET

# --------------------------------------------------------------------------------------
#   custom
# --------------------------------------------------------------------------------------
#
# StatusManager - supporting definitions for error management
#   error message generation routines -
#     err_to_str - for displaying messages in exception objects
#     errmsg - standardize error messages by indicating the name of the problem file
#   exit status code management -
#     a collection of setter routines
#     status() - return final status
# CONSTANTS - supporting definitions for forms parsing
#   CONFIG_FILE_KEY -    key to XML file for overriding selected default values
#   CONFIG_SCHEMA_KEY -  key to XML file for validating configuration files
# DEFAULTS - supporting definitions for forms parsing
#   MERGER_CONFIG - XML file default values

import src.StatusManager as STATUS
import src.CONSTANTS     as CONST
import src.DEFAULTS      as DEFAULT

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
    print( STATUS.errmsg( err_msg, True ), file=sys.stderr )
    sys.exit( STATUS.ExitStatus.improper_environmental_configuration() )


# ***********************************************
# main module
# ***********************************************

# ==========================================================================================================================
# asXML - map Python content to an XML document
#
# Parameters:
# -.  name of top-level element for XML tree
# -.  contents, as possibly recursive list of dictionaries or (key, value) pairs
# -.  logger - for generating error messages
# ==========================================================================================================================

# --------------------------------------------------------------------------------------------------------------------------
# Auxiliary routines for use by this and other modules
#
# -.  xml_declaration - constant for acquiring a document's leading xml declaration
# -.  open_tag, close_tag - generate open and close tags from an XML-compatible identifier (assumed)
# -.  make_elt - make an XML element from a (key, value) pair
# -.  prettyPrint - pretty print an XML document's content, optionally specifying its level-by-level indentation
# --------------------------------------------------------------------------------------------------------------------------

xml_declaration = '<?xml version="1.0" ?>'

open_tag =  lambda key: f"<{str(key).lower()}>"
close_tag = lambda key: f"</{str(key).lower()}>"

make_elt = lambda key, value: (
    f"<{str(key).lower()}/>"
    if value is None
    else f"<{str(key).lower()}>{str(value).strip(' ')}</{str(key).lower()}>"
)

prettyPrint = lambda content, indent="    ": "\n".join( line for line in MINIDOM.parseString(content).toprettyxml(indent).split("\n") if line.strip() )

# --------------------------------------------------------------------------------------------------------------------------
# asXML proper
#---------------------------------------------------------------------------------------------------------------------------

def asXML(outer_tag, content, logger):
    def asXMLcontent(stuff):
        if isinstance(stuff, dict):
            return asXMLcontent(list(stuff.items()))
        # Assume that a pair of values with an atomic first value is a key-value pair
        if (len(stuff) == 2) and isinstance(stuff[0], (str, int)):
            if isinstance(stuff[1], (str, int, type(None))):
                return make_elt(
                    stuff[0],
                    None if stuff[1] is None else str(stuff[1]).replace("&", "&amp;").replace("<", "&lt;")
                )
            return make_elt(stuff[0], asXMLcontent(stuff[1]))
        if isinstance(stuff, list):
            return "".join([asXMLcontent(item) for item in stuff])
        err_msg = f"asXML: malformed (key, value) structure ({content}) - exiting\n"
        err_msg += f"asXML: problem subexpression - {stuff}\n"
        error_message = STATUS.errmsg( err_msg )
        logger.error( error_message )
        STATUS.ExitStatus.internal_error()
        raise STATUS.InternalError( err_msg )
    return prettyPrint( make_elt( outer_tag, asXMLcontent(content)) )


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
    def __init__( self, config_file=DEFAULT.MERGER_CONFIG[CONST.CONFIG_FILE_KEY], config_schema=DEFAULT.MERGER_CONFIG[CONST.CONFIG_SCHEMA_KEY] ):
        #
        self._contents = {}
        self.file_missing = []
        self.file_malformed = []
        self.schema_missing = []
        self.schema_malformed = []
        self.file_invalid = []
        #
        # step 1 - try to retrieve file's contents as a dictionary
        #
        if not Path(config_file).is_file():
            self.file_missing = [ f"XMLFile: config file {config_file} not found" ]
        else:
            try:
                parsed_config_file = ET.parse(config_file)
                self._contents = dict( [(e.tag, e.text) for e in parsed_config_file.iterfind("./*")] )
            except xml.etree.ElementTree.ParseError as e:
                self.file_malformed = [ f"XMLFile: cannot parse {config_file} - {STATUS.err_to_str(e)}" ]
        #
        # step 2  - try to validate the schema
        #
        if not Path(config_schema).is_file():
            self.schema_missing = [ f"XMLFile: config schema {config_schema} not found" ]
        else:
            try:
                parsed_config_file_schema = xmlschema.XMLSchema(config_schema)
            except Exception as e:
                self.schema_malformed = [ f"XMLFile: invalid schema {config_schema} - {STATUS.err_to_str(e)}" ]
        #
        # step 3 - validate the file
        #
        if self.file_missing or self.file_malformed or self.schema_missing or self.schema_malformed: return
        try:
            parsed_config_file_schema.validate(config_file)
        except Exception as e:
            self.file_invalid = [ f"XMLFile: schema {config_schema} won't validate {config_file} - {STATUS.err_to_str(e)}" ]

    def contents(self):
        return (
            self._contents,
            self.file_missing,
            self.file_malformed,
            self.schema_missing,
            self.schema_malformed,
            self.file_invalid,
        )
