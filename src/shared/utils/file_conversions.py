import os

from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Union


class FileOpts(Enum):
    JSON = auto()
    PICKLE = auto()
    TXT = auto()

def remove_suffix(file_name: Union[str, Path]) -> str:
    if isinstance(file_name, str):
        file_name = Path(file_name)
    as_posix = file_name.as_posix()
    return as_posix.removesuffix(file_name.suffix)

def validate_save_dir(dir_to_validate: str):
    if not os.path.exists(dir_to_validate):
                os.makedirs(dir_to_validate)
    if not os.path.isdir(dir_to_validate):
        raise ValueError(f"Expected the specified save path to be a directory, instead got: {dir_to_validate}")

def replace_suffix(file_name: Path, file_type: FileOpts) -> str:
    converted_filename = remove_suffix(file_name=file_name)

    match file_type:
        case FileOpts.JSON:
            converted_filename = converted_filename + ('.json')
        case FileOpts.PICKLE:
            converted_filename = converted_filename + ('.pkl')
        case FileOpts.TXT:
            converted_filename = converted_filename + ('.txt')
        case _:
            raise TypeError(f"The file type passed to replace_suffix was not recognized: {file_type}")
    return converted_filename





class FileConverter(ABC):
    class ConversionOptions(Enum):
        ...

    @property
    @abstractmethod
    def default_options(self) -> Dict[ConversionOptions, Any]:
        """Subclasses must define this"""
        pass

    def get_opt(self, option: ConversionOptions) -> Any:
        return self.default_options.get(option, None)

    @staticmethod
    def save_as(save_to_dir: str, raw_basename: str, ftype: FileOpts, object_to_save, keep_suffix: bool = False):

        dir_obj = Path(save_to_dir)

        posix_dirname = dir_obj.as_posix()

        validate_save_dir(posix_dirname)

        if not keep_suffix:
            basename_obj = Path(raw_basename)
            converted_filename = replace_suffix(file_name=basename_obj, file_type=ftype)
        else:
            converted_filename = raw_basename

        FileConverter._assert_type(object_to_assert=object_to_save, type_to_assert=ftype)
        fullpath = os.path.join(posix_dirname, converted_filename)

        match ftype:
            case FileOpts.JSON:
                with open(fullpath, "wb") as f:
                    f.write(object_to_save)
            case FileOpts.PICKLE:
                with open(fullpath, "wb") as f:
                    f.write(object_to_save)
            case FileOpts.TXT:
                with open(fullpath, "w", encoding='utf-8') as f:
                    f.write(object_to_save)
            case _:
                raise TypeError(f"Unsupported file type: {ftype}")
        return fullpath

    @staticmethod
    def update_options(options_to_update: Dict[ConversionOptions, Any], base_options: Dict[ConversionOptions, Any]):
        new_opts = base_options.copy()
        new_opts.update({k: v for k, v in options_to_update.items() if v is not None})
        return new_opts

    @staticmethod
    def _assert_type(object_to_assert, type_to_assert: FileOpts):
        match type_to_assert:
            case FileOpts.JSON:
                if not isinstance(object_to_assert, bytes):
                    raise TypeError(f"Expected a bytes-like object for conversion to JSON. Recieved: {object_to_assert}")
            case FileOpts.PICKLE:
                if not isinstance(object_to_assert, bytes):
                    raise TypeError(f"Expected a bytes-like object for conversion to Pickle. Recieved: {type(object_to_assert)}")
            case FileOpts.TXT:
                # This might be debugging output, so we are going to remain agnostic on the type we are printing.
                ...
            case _:
                raise TypeError(f"Type assertion called for FileConverter, but an unsupported type was passed: {type_to_assert}")
