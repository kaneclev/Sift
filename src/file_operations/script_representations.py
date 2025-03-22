from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, List

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
    NotAFileError,
    SiftFileDoesNotExistError,
)


class RepresentationType(Enum):
    FILE = auto()
    QUEUE = auto()

@dataclass
class ScriptObjectIssues:
    issues: List[Exception] = field(default_factory=list)

    def append(self, exception: Exception):
        self.issues.append(exception)

    def describe(self):
        reason_list: List[str] = []
        reason_list.extend([str(issue) for issue in self.issues])
        return "\n".join(reason_list)

@dataclass
class ScriptContent:
    content: Any

class ScriptObject(ABC):
    def __init__(self, to_verify: Any):
        self.issues = ScriptObjectIssues()
        self.is_verified = self.verify(to_verify)
        self.data: ScriptContent = None

    @abstractmethod
    def verify(self, to_verify: Any) -> bool:
        ...

    def get_content(self) -> Any:
        assert self.is_verified
        return self.data.content

    @abstractmethod
    def get_id(self):
        ...

class File(ScriptObject):
    @dataclass
    class Metadata:
        last_modified: datetime
        name: str
        directory: str
    @dataclass
    class SiftFileContent(ScriptContent):
        content: str
        metadata: 'File.Metadata'

    def __init__(self, file_path: str):
        self.path_obj = None
        super().__init__(to_verify=file_path)
        self.metadata: File.Metadata = self._get_metadata()
        self.data = self.get_data()

    def verify(self, path_to_verify: str) -> bool:
        self.path_obj = Path(Path(path_to_verify).as_posix())
        self._verify_filepath(file_path=self.path_obj)
        if self.issues.issues:
            return False
        return True

    def _get_metadata(self) -> Metadata:
        assert isinstance(self.path_obj, Path)
        last_mod = self.path_obj.stat().st_mtime
        last_mod_datetime = datetime.fromtimestamp(last_mod)
        file_name = self.path_obj.name
        directory = self.path_obj.parent
        return File.Metadata(last_modified=last_mod_datetime, name=file_name, directory=directory)

    def get_data(self) -> 'File.SiftFileContent':
        if not self.data:
            content = None
            with open(self.path_obj, 'r') as file:
                content = file.read()
            if content is None:
                raise ValueError(f"File {self.path_obj} does not have any data or could not be read")
            self.data = File.SiftFileContent(content=content, metadata=self.metadata)
        return self.data

    def get_id(self):
        return self.metadata.name

    def _verify_filepath(self, file_path: Path) -> None:
        assert isinstance(file_path, Path)
        if not file_path.exists():
            exception = SiftFileDoesNotExistError(file_path)
            self.issues.append(exception=exception)
        if not file_path.is_file():
            exception = NotAFileError(file_path)
            self.issues.append(exception=exception)
        if file_path.suffix != ".sift":
            exception = BadExtensionError(file_path)
            self.issues.append(exception=exception)


def get_script_object(raw: Any, rtype: RepresentationType) -> ScriptObject:
    match rtype:
        case RepresentationType.FILE:
            assert isinstance(raw, str)
            return File(raw)
        case _:
            ...
    return None
