import logging
# The importlib module provides a way to import other modules dynamically
from importlib import import_module
# The inspect module provides functions for inspecting live objects such as modules, classes, and functions
from inspect import getmembers, isabstract, isclass

from src.transcribe.models import Transcribe

logger = logging.getLogger(__name__)

# Define the TranscribeFactory class
class TranscribeFactory:
    @staticmethod
    def load_class(module_name) -> Transcribe:
        try:
            # Attempt to import the specified module
            # The "." prefix means that the module should be searched for in the same package as this file
            # The "src.transcribe.models" argument specifies the package and subpackage where the module can be found
            logger.info("Importing module " + module_name)
            factory_module = import_module("." + module_name, "src.transcribe.models")
        except ImportError as e:
            # If there's an ImportError, print an error message and return None
            logger.error("Error importing module " + module_name, e)
            return 

        # Get all classes defined in the module that are not abstract
        # and are subclasses of Transcribe
        classes = getmembers(factory_module, lambda m: isclass(m) and not isabstract(m))

        # Loop through the classes and return the first one found
        for name, _class in classes:
            return _class()
        
        # If no class was found, return None
        return 
