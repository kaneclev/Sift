class BaseFileError(Exception):
    def __init__(self, filepath, *args):
        super().__init__(*args)
        self.filepath = filepath

class BadExtensionError(BaseFileError):
    def __init__(self, filepath, *args):
        super().__init__(filepath, *args)
    def __str__(self):
        return f"Expected a .sift file, but got: {self.filepath}"

class SiftFileDoesNotExistError(BaseFileError):
    def __init__(self, filepath, *args):
        super().__init__(filepath, *args)
    def __str__(self):
        return f"No such .sift file exists: {self.filepath}"

