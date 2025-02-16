from pathlib import Path
from typing import Union


class BaseFileError(Exception):
    """ The base class for the File exception type.

    *Not to be raised directly; purely heritable.*
    """
    def __init__(self, filepath: Union[Path, str]):
        """ The constructor for the BaseFileError class.

        Stores the filepath to the offending file which caused the exception.

        Args:
            filepath (Union[Path, str]): The path to the offending file.
        """
        super().__init__()
        self.filepath = filepath

class BadExtensionError(BaseFileError):
    """ Raised when a file has the incorrect extension in a context.

    *Inherits from the BaseFileError class.*
    """
    def __init__(self, filepath: Union[Path, str]):
        """ Given the path to the bad-extensioned file, creates a BadExtensionError instance.

        Args:
            filepath (Union[Path, str]): The offending file path, passed to the BaseFileError class.
        """
        super().__init__(filepath)
    def __str__(self):
        """ The error message for the BadExtensionError exception.

        Returns:
            str: The error message.
        """
        return f"Expected a .sift file, but got: {self.filepath}"

class NotAFileError(BaseFileError):
    """ Raised when the path passed in a context was expected to be a file, but was not.

    *Inherits from the BaseFileError class.*
    """
    def __init__(self, filepath: Union[Path, str]):
        """ Given the non-file path, creates a NotAFileError instance.

        Args:
            filepath (Union[Path, str]): The offending file path, passed to the BaseFileError class.
        """
        super().__init__(filepath)
    def __str__(self):
        """ The error message for the NotAFileError exception.

        Returns:
            str: The error message.
        """
        return f"Expected a file, but got: {self.filepath}"

class SiftFileDoesNotExistError(BaseFileError):
    """ Raised when the path to a Sift file does not exist.

    *Inherits from the BaseFileError class.*
    """
    def __init__(self, filepath: Union[Path, str]):
        """ Given the non-existent Sift file path, creates a SiftFileDoesNotExistError instance.

        Args:
            filepath (Union[Path, str]): The offending file path, passed to the BaseFileError class.
        """
        super().__init__(filepath)
    def __str__(self):
        """ The error message for the SiftFileDoesNotExistError exception.

        Returns:
            str: The error message.
        """
        return f"No such .sift file exists: {self.filepath}"

class BadPluginNameError(BaseFileError):
    """ Raised when a plugin filename for a Sift operation is invalid for some reason.

    *Inherits from the BaseFileError class.*
    """
    def __init__(self, filepath: Union[Path, str]):
        """ Given the invalid plugin file path, creates a BadPluginNameError instance.

        Args:
            filepath (Union[Path, str]): The offending file path, passed to the BaseFileError class.
        """
        super().__init__(filepath)
    def __str__(self):
        """ The error message for the BadPluginNameError exception.

        Returns:
            str: The error message.
        """
        return f"Unreadable plugin file: {self.filepath} (expected to be a .py file)"

class PluginNotFoundError(BaseFileError):
    """ Raised when a plugin was expected to exist, but the file was not found in the project.

    *Inherits from the BaseFileError class.*
    """
    def __init__(self, expected_plugin: str):
        """ Given the expected plugin name that is utilized in the Sift script, creates a PluginNotFoundError instance.

        Args:
            expected_plugin (str): The expected plugin name that was not found.
        """
        self.expected_plugin = expected_plugin
        super().__init__(filepath="")
    def __str__(self):
        """ The error message for the PluginNotFoundError exception.

        Returns:
            str: The error message.
        """
        return f"No such plugin detected under the name: {self.expected_plugin}"
