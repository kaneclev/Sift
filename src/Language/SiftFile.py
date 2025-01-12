from pathlib import Path
from Language.HighLevelStructure.HighLevelTree import HighLevelTree
import Language.Exceptions.SiftFileExceptions as SFE


class SiftFile:
    def __init__(self, file_path: Path, test_mode: bool = False):
        self.file_path = file_path
        self.data = None
        self.high_level_structure = None
        if test_mode:
            pass

        self._verify()
        self.data = self._parse_file()  
        self.high_level_structure = self._make_tree(self.data)

    def _verify(self):
        self.validate_correct_path_type()
        self.verify_filepath()

    def _make_tree(self, data):
        return HighLevelTree(data)
    
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
    
    def _parse_file(self):
        with open(self.file_path, 'r') as file:
            return file.read()
        
    def raise_issues(self, exceptions: list[Exception]):
        if exceptions:
            raise SFE.ExceptionList(exception_list=exceptions)
    
    def validate_correct_path_type(self):
        if not isinstance(self.file_path, Path):
                    if isinstance(self.file_path, str):
                        self.file_path = Path(self.file_path)
                    else:
                        raise SFE.BadArgumentTypeException(self.file_path)
    
    def show_tree(self):
        return self.high_level_structure.print_tree()
