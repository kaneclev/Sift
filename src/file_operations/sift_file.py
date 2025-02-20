import os

from pathlib import Path
from typing import Union

import file_operations.exceptions.internal.internal_exceptions as foie

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
    NotAFileError,
    SiftFileDoesNotExistError,
)
from language.parsing.ast.ast_json_converter import SiftASTConverter
from language.parsing.ast.script_tree import ScriptTree
from language.parsing.parser import Parser


class SiftFile:
    """ The interface for creating and parsing a sift script.
    The SiftFile class takes a filepath parameter into its constructor, validates the path,
    and then offers API methods for parsing and converting a sift script into a structured JSON format.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = None
        self.parser = None
        self.tree = None

        self._verify()

    def sift_script_to_json(self) -> str:
        """ Morphs the already-parsed sift script tree into JSON format.

        Keyword arguments:
        Takes no arguments, but it is expected that parse_file has already been called on the instance.
        Return: A JSON representation of the sift script tree. (string)
        """
        # If parse_file hasn't been called on us yet...
        if not self.tree:
            raise ValueError("No tree has been generated...")
        else:
            # Use the SiftASTConverter class, with the to_json method, to return the JSON representation.
            converter = SiftASTConverter(self.tree, filename=os.path.basename(self.file_path))
            return converter.to_json()

    def parse_file(self) -> ScriptTree:
        """ The main API method of the SiftFile. Performs the full conversion from file to ScriptTree (AST) object.

        Keyword arguments:
        None
        Return: ScriptTree object, as well as updates the instance's 'tree' member variable with the value of the ScriptTree.
        """

        self.data = self._read_file()
        self.parser = Parser(self.data)
        self.tree = self._generate_parse_tree()
        if self.tree is None:
            raise ValueError("There was an issue with the creation of the Parser object \
                             *or* the process of parsing this instance's content to a ScriptTree.")
        return self.tree

    def _generate_parse_tree(self) -> Union[Parser, None]:
        """ Internal helper method for the parse_file API function.
        Uses the instance's Parser object, which was defined in the parse_file before our call,
        to parse our instance's 'data' member into a ScriptTree object.

        Keyword arguments:
        None.
        Return:
            ScriptTree if self.parser was created succesffully.
            None otherwise.
        """

        if self.parser:
            return self.parser.parse_content_to_tree()
        return None

    def _verify(self) -> None:
        """ Helper method which calls other utility functions for verifying the validity of a Sift file.

        Keyword arguments:
        None.
        Return:
            None, but an exception will be raised by one of the callee's if there is a validation issue.
        """

        self._validate_correct_path_type()
        self._verify_filepath()

    def _read_file(self) -> str:
        """ Utility method for reading in the *validated* sift file.

        Keyword arguments:
        None.
        Return: The contents of the sift file (str)
        """

        with open(self.file_path, 'r') as file:
            return file.read()

    def _verify_filepath(self) -> None:
        """ Uses package methods for a Path object to verify the validity of a provided filepath.

        Keyword arguments:
        None.
        Return:
            None, but raises an *external* exception if a path fails validation for any of the reasons
            below.
        """

        if not self.file_path.exists():
            raise SiftFileDoesNotExistError(self.file_path)
        if not self.file_path.is_file():
            raise NotAFileError(self.file_path)
        if self.file_path.suffix != ".sift":
            raise BadExtensionError(self.file_path)

    def _validate_correct_path_type(self) -> None:
        """ Forces the correct type for the filepath passed to the constructor.

        Keyword arguments:
        None.
        Return:
            None, but raises an *internal* exception if the member's file_path type is not correct.
        """

        if not isinstance(self.file_path, Path):
                    if isinstance(self.file_path, str):
                        self.file_path = Path(self.file_path)
                    else:
                        raise foie.BadTypeError(method="validate_correct_path_type",
                                           class_="SiftFile",
                                           field="self.file_path",
                                           expected_type="Path",
                                           given_type=str(type(self.file_path)))

    def show_tree(self) -> None:
        """ Debugging method for displaying the ScriptTree object in a human-friendly manner.

        Keyword arguments:
            None.
        Return:
            The str() return value of the instances ScriptTree (string)
            If the instance's ScriptTree object has not been generated yet, returns None.
        """

        if isinstance(self.tree, ScriptTree):
            print(str(self.tree))

    def get_tree_obj(self) -> Union[ScriptTree, None]:
        """ Returns the instance's ScriptTree object.

        Keyword arguments:
        None.
        Return: self.tree, the instances ScriptTree member (potentially None).
        """

        return self.tree
