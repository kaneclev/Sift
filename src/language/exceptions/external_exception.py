from pathlib import Path
from typing import Dict, Union


class ExternalExceptionError(Exception):
    """Base class for external-facing exception hierarchy.

    *Not to be raised directly; serves as foundation for specific error types.*
    """
    def __init__(self, *args):
        """Initializes external exception with flexible arguments.

        Args:
            *args: Variable length argument list passed to base Exception class
        """
        super().__init__(*args)

class MultipleDefinitionsError(ExternalExceptionError):
    """Raised when multiple conflicting definitions exist for a feature.

    *Inherits from ExternalExceptionError.*
    """
    def __init__(self, single_definition_feature: str, original_definition: str,
                 offending_alternate_definitions: list):
        """Records definition conflict details.

        Args:
            single_definition_feature (str): Name of the multiply-defined feature
            original_definition (str): First/valid definition encountered
            offending_alternate_definitions (list): Conflicting alternative definitions
        """
        self.offending_feature = single_definition_feature
        self.original_definition = original_definition
        self.offending_alternate_definitions = offending_alternate_definitions
        super().__init__()

    def __str__(self) -> str:
        """Formats definition conflict message.

        Returns:
            str: Structured error message showing original vs alternatives
        """
        return f"Multiple definitions for '{self.offending_feature}'; \
                    \n\t Original Definition: {self.original_definition} \
                    \n\t New Definitions: {self.offending_alternate_definitions}"

class MultipleTargetListDefinitionsError(MultipleDefinitionsError):
    """Specialized error for conflicting 'targets' list definitions.

    *Inherits from MultipleDefinitionsError.*
    """
    def __init__(self, original_definition: str, offending_alternate_definitions: list):
        """Processes target list conflicts into readable format.

        Args:
            original_definition (str): Valid target list definition
            offending_alternate_definitions (list): Conflicting target definitions
        """
        # Convert list to pipe-separated string
        offending_alternate_definitions_string = " | ".join(offending_alternate_definitions)
        # Add context prefix to alternative definitions
        formatted_offending_alternate_definitions_string = "Alternate definitions: ".join(
            [offending_alternate_definitions_string]
        )

        super().__init__(
            "targets",
            original_definition,
            formatted_offending_alternate_definitions_string
        )
class SyntaxError(ExternalExceptionError):
    def __init__(self, context: Dict):
        self.offense = context["offense"]
        self.col = context["col"]
        self.line = context["line"]
        self.expected: Dict[str, str] = context["expected"]
        self.pretty_expected = []

        for exp_rule, _ in self.expected.items():
            self.pretty_expected.append(f"'{exp_rule}'")

        self.expected = " ".join(self.pretty_expected)

    def __str__(self):
        reason = [
            f"Unexpected values: '{self.offense}' at line {self.line}, column {self.col}. "
            f"Expected one of: {self.expected}"
        ]
        return "\n".join(reason)



class BaseFileError(Exception):
    """ The base class for the File exception type.

    *Not to be raised directly; purely inheritable.*
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
