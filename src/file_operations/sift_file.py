from pathlib import Path

import file_operations.exceptions.internal.internal_exceptions as foie

from language.parsing.parser import Parser

""" #TODO Modify Exceptions to use the new internal/external exceptions.

Keyword arguments:
argument -- description
Return: return_description
"""

class SiftFile:
    def __init__(self, file_path: Path, test_mode: bool = False):
        self.file_path = file_path
        self.data = None
        self.parser = None
        self.tree = None
        if test_mode:
            pass

        self._verify()
        self.data = self._read_file()
        self.parser = Parser(self.data)
        self.tree = self.generate_parse_tree()

    def _verify(self):
        self.validate_correct_path_type()
        self.verify_filepath()

    def verify_filepath(self):
        exceptions = []
        if not self.file_path.exists():
            exceptions.append(FileNotFoundError(f"The file path: {self.file_path} does not exist."))
        if not self.file_path.is_file():
            exceptions.append(ValueError(f"The file path: {self.file_path} is not a file."))
        if self.file_path.suffix != ".sift":
            exceptions.append(ValueError(f"The file path: {self.file_path} is not a sift file (no .sift extension)"))
        if exceptions:
            self.raise_issues(exceptions=exceptions)

    def _read_file(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def raise_issues(self, exceptions: list[Exception]):
        if exceptions:
            raise foie.ExceptionList(exception_list=exceptions)

    def validate_correct_path_type(self):
        if not isinstance(self.file_path, Path):
                    if isinstance(self.file_path, str):
                        self.file_path = Path(self.file_path)
                    else:
                        raise foie.BadType(method="validate_correct_path_type",
                                           class_="SiftFile",
                                           field="self.file_path",
                                           expected_type="Path",
                                           given_type=str(type(self.file_path)))

    def generate_parse_tree(self):
        if self.parser:
            return self.parser.parse_content_to_tree()
        return None

    def show_tree(self):
        if self.tree:
            return str(self.tree)

    def get_tree_obj(self):
        return self.tree
