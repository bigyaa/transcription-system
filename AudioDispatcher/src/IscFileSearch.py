# *************************************************************************************************************************
#   IscFileSearch.py
#       This module provides the IscFileSearch class that offers methods to interact with the file system.
#       It includes functionalities to search, delete, rename, and retrieve properties of files, with a focus on audio files.
# -------------------------------------------------------------------------------------------------------------------
#   Usage:
#       The IscFileSearch class can be instantiated with a directory path. It provides methods to traverse directories,
#       get files by extension, delete files, rename files with optional overwrite, and get file properties.
#
#       Parameters:
#           path - The directory path where the file operations will be performed.
#           file_exts - A list of file extensions to filter files by during searches.
#           old_name, new_name - The old and new names of a file for the rename operation.
#           overwrite - A boolean indicating whether to overwrite an existing file during renaming.
#
#       Outputs:
#           The class methods return lists of file paths, status codes for file operations, and dictionaries of file properties.
#
#   Design Notes:
#   -.  Error handling is built into the methods to log issues when file operations fail.
#   -.  The os module is used for file system interactions, and logging is used for error and info messages.
# ---------------------------------------------------------------------------------------------------------------------
#   last updated: January 2024
#   authors: Ruben Maharjan, Bigya Bajarcharya, Mofeoluwa Jide-Jegede
# *************************************************************************************************************************
# ***********************************************
# imports
# ***********************************************

# os - module providing a portable way of using operating system dependent functionality
#    os.path - submodule of os for manipulating paths
#    os.walk - function to generate the file names in a directory tree
#    os.listdir - function to list the files in a directory
#    os.remove - function to remove a file
#    os.rename - function to rename a file
#    os.stat - function to get the status of a file

# logging - module to provide logging functionalities
#    getLogger - function to return a logger instance

import logging
import os

logger = logging.getLogger()

class IscFileSearch:
    """
    The IscFileSearch class provides methods to interact with the file system, with a focus on audio files.

    Attributes:
        path (str): The directory path where file operations will be performed.

    Methods:
        traverse_directory(): Recursively traverses a directory and returns a list of audio file paths.
        get_files(file_exts=None): Returns a list of audio file paths filtered by specified extensions.
        delete_file(file_path): Deletes a file at the specified path.
        rename_file(old_name, new_name, overwrite=False): Renames a file and returns a status code.
        get_file_properties(file_path): Returns a dictionary of properties for the file at the specified path.
    """

    def __init__(self, path):
        """
        Initialize the IscFileSearch with a directory path.

        Args:
            path (str): The directory path.
        """
        self.path = path
    
    def traverse_directory(self):
        """
        Recursively traverses a directory and returns a list of audio file paths for files ending with .mp3 or .wav.
        """
        if not os.path.exists(self.path):
            logger.error("Directory does not exist: %s", self.path)
            return []

        audio_file_paths = []
        self._traverse_directory_recursively(self.path, audio_file_paths)
        return audio_file_paths

    def _traverse_directory_recursively(self, directory, audio_file_paths):
        """
        Recursively traverses a directory and adds audio file paths to the provided list.
        """
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isdir(filepath):
                self._traverse_directory_recursively(filepath, audio_file_paths)
            elif filename.lower().endswith(('.mp3', '.wav')):
                audio_file_paths.append(filepath)

    def get_files(self, file_exts=None):
        """
        Returns a list of audio file paths in the directory filtered by specified file extensions.

        Args:
            file_exts (list): A list of file extensions to filter files by during searches.

        Returns:
            list: List of audio file paths.
        """
        if file_exts is None:
            file_exts = ['mp3', 'wav']
        return [file_path for file_path in self.traverse_directory() if file_path.lower().endswith(tuple(file_exts))]

    def delete_file(self, file_path):
        """
        Deletes a file at the specified path.

        Args:
            file_path (str): The path of the file to be deleted.
        """
        try:
            os.remove(file_path)
            logger.info("File deleted: %s", file_path)
        except FileNotFoundError:
            logger.error("File does not exist: %s", file_path)
        except OSError as e:
            logger.error("Error deleting file %s: %s", file_path, e)

    def rename_file(self, old_name, new_name, overwrite=False):
        """
        Renames a file from old_name to new_name and returns a status code.

        Args:
            old_name (str): The old name of the file.
            new_name (str): The new name of the file.
            overwrite (bool): Whether to overwrite an existing file with the new name.

        Returns:
            int: Status code (0: Success, 1: Old file not found, 2: New file already exists, 3: Rename failed).
        """
        old_path = os.path.join(self.path, old_name)
        new_path = os.path.join(self.path, new_name)

        if not os.path.exists(old_path):
            logger.error("File does not exist: %s", old_path)
            return 1
        if os.path.exists(new_path) and not overwrite:
            logger.warning("File already exists with new name: %s", new_name)
            return 2

        try:
            os.rename(old_path, new_path)
            logger.info("File renamed from %s to %s", old_name, new_name)
            return 0
        except OSError as e:
            logger.error("Failed to rename file %s to %s: %s", old_name, new_name, e)
            return 3

    def get_file_properties(self, file_path):
        """
        Returns a dictionary of properties for the file at the specified path.

        Args:
            file_path (str): The path of the file.

        Returns:
            dict: Dictionary of file properties.
        """
        try:
            file_stats = os.stat(file_path)
            return {
                "file_name": os.path.basename(file_path),
                "file_size": file_stats.st_size,
                "creation_time": file_stats.st_ctime,
                "modified_time": file_stats.st_mtime,
                "access_time": file_stats.st_atime,
            }
        except FileNotFoundError:
            logger.error("File does not exist: %s", file_path)
            return None
        except OSError as e:
            logger.error("Error accessing file properties for %s: %s", file_path, e)
            return None
