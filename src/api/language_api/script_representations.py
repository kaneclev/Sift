from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, List, Union


class RepresentationType(Enum):
    FILE = auto()
    MESSAGE = auto()

@dataclass
class Issue:
    exception: Exception
    reason: str
    def __str__(self):
        return f"\t{self.exception}. Reason: {self.reason}"
@dataclass
class ScriptObjectIssues:
    issues: List[Issue] = field(default_factory=list)

    def append(self, issue: Issue):
        self.issues.append(issue)

    def get_issues(self) -> List[Issue]:
        return self.issues

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
        if not self.is_verified:
            return
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
        if file_path.suffix != ".sift":
            exception = NameError(file_path)
            self.issues.append(issue=Issue(exception=exception, 
                                           reason="No '.sift' extension present; is this the right filetype?"))
        if not file_path.exists():
            exception = FileNotFoundError(file_path)
            self.issues.append(issue=Issue(exception=exception, 
                                           reason="This sift file doesn't exist."))
            return # Because we know it wont be a file.
        if not file_path.is_file():
            exception = TypeError(file_path)
            self.issues.append(issue=Issue(exception=exception, 
                                           reason="This sift file is not a regular file (is it a directory?)"))
        

class Message(ScriptObject):
    def __init__(self, content, correlation_id):
        super().__init__(to_verify=content)
        self.correlation_id = correlation_id
        self.data = ScriptContent(content=content)

    def verify(self, to_verify: str):
        if to_verify.strip() is not None:
            return True
        self.issues.append(issue=Issue(exception=ValueError(), reason="No content present in the script message."))
        return False

    def get_id(self):
        return self.correlation_id

def get_script_object(raw: Any, rtype: RepresentationType) -> Union[ScriptObject, ScriptObjectIssues]:
    match rtype:
        case RepresentationType.FILE:
            assert isinstance(raw, str)

            new_file = File(raw)
            if not new_file.is_verified:
                return new_file.issues
            return new_file
        case RepresentationType.MESSAGE:
            assert isinstance(raw, dict)

            correlation_id = raw["correlation_id"]
            content = raw["script_content"]
            new_script_msg = Message(content=content, correlation_id=correlation_id)

            if not new_script_msg.is_verified:
                return new_script_msg.issues

            return new_script_msg
        case _:
            raise TypeError(f"Unexpected representation type: {rtype} (object: {raw})")
    return None
