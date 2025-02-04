class BaseFileError(Exception):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

class BadExtensionError(BaseFileError):
    def __init__(self, filepath):
        super().__init__(filepath)
    def __str__(self):
        return f"Expected a .sift file, but got: {self.filepath}"

class NotAFileError(BaseFileError):
    def __init__(self, filepath):
        super().__init__(filepath)
    def __str__(self):
        return f"Expected a file, but got: {self.filepath}"
class SiftFileDoesNotExistError(BaseFileError):
    def __init__(self, filepath):
        super().__init__(filepath)
    def __str__(self):
        # ! Note: The cwd for SiftFile when it looks for the file is src/
        return f"No such .sift file exists: {self.filepath}"

class BadPluginNameError(BaseFileError):
    def __init__(self, filepath):
        super().__init__(filepath)
    def __str__(self):
        return f"Unreadable plugin file: {self.filepath}"

class PluginNotFoundError(BaseFileError):
    def __init__(self, filepath):
        super().__init__(filepath)
    def __str__(self):
        return f"No such plugin detected under the name: {self.filepath}"
