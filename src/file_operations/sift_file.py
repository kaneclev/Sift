from pathlib import Path

import file_operations.exceptions.internal.internal_exceptions as foie

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
    NotAFileError,
    SiftFileDoesNotExistError,
)
from language.parsing.parser import Parser


class SiftFile:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = None
        self.parser = None
        self.tree = None

        self._verify()

    def parse_file(self):
        self.data = self._read_file()
        self.parser = Parser(self.data)
        self.tree = self._generate_parse_tree()

    def _generate_parse_tree(self):
        if self.parser:
            return self.parser.parse_content_to_tree()
        return None

    def _verify(self):
        self.validate_correct_path_type()
        self.verify_filepath()

    def _read_file(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def verify_filepath(self):
        if not self.file_path.exists():
            raise SiftFileDoesNotExistError(self.file_path)
        if not self.file_path.is_file():
            raise NotAFileError(self.file_path)
        if self.file_path.suffix != ".sift":
            raise BadExtensionError(self.file_path)

    def validate_correct_path_type(self):
        if not isinstance(self.file_path, Path):
                    if isinstance(self.file_path, str):
                        self.file_path = Path(self.file_path)
                    else:
                        raise foie.BadTypeError(method="validate_correct_path_type",
                                           class_="SiftFile",
                                           field="self.file_path",
                                           expected_type="Path",
                                           given_type=str(type(self.file_path)))

    def show_tree(self):
        if self.tree:
            return str(self.tree)

    def get_tree_obj(self):
        return self.tree
