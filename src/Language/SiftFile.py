from pathlib import Path
from CstmParseTree import ParseTree

class SiftFile:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = None  # This will hold the structured representation
        self._parse_file()
    
    def verify_filepath(self):
        exceptions = []
        if not self.file_path.exists():
            exceptions.append(FileNotFoundError(f"The file path: {self.file_path} does not exist."))
        if not self.file_path.is_file():
            exceptions.append(ValueError(f"The file path: {self.file_path} is not a file."))
        if self.file_path.suffix != ".sift":
            exceptions.append(ValueError(f"The file path: {self.file_path} is not a sift file (no .sift extension)"))
        return exceptions
    
    def _parse_file(self):
        exceptions = self.verify_filepath()
        if exceptions:
            raise Exception(f"File verification failed with errors: {exceptions}")
        
        with open(self.file_path, 'r') as file:
            file_contents = file.read()
        
        ParseTree(file_contents)
        exit()
        
        # Transform the parse tree into a structured object



a = SiftFile(Path(r"C:\Users\Kane\projects\Sift\siftscripts\example.sift"))