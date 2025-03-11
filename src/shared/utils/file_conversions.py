import os

from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict


class FileOpts(Enum):
    JSON = auto()

def validate_save_dir(dir_to_validate: str):
    if not os.path.exists(dir_to_validate):
                os.makedirs(dir_to_validate)
    if not os.path.isdir(dir_to_validate):
        raise ValueError(f"Expected the specified save path to be a directory, instead got: {dir_to_validate}")

def replace_suffix(file_name: Path, file_type: FileOpts) -> str:
    match file_type:
        case FileOpts.JSON:
            extension = file_name.suffix
            posix_basename = file_name.as_posix()
            converted_filename = posix_basename.removesuffix(extension)
            converted_filename = converted_filename = converted_filename + ('.json')
            return converted_filename
        case _:
            raise TypeError(f"The file type passed to replace_suffix was not recognized: {file_type}")



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
    def _save_as(save_to_dir: str, raw_basename: str, ftype: FileOpts, object_to_save):

        dir_obj = Path(save_to_dir)

        posix_dirname = dir_obj.as_posix()

        basename_obj = Path(raw_basename)

        validate_save_dir(posix_dirname)

        converted_filename = replace_suffix(file_name=basename_obj, file_type=ftype)

        match ftype:
            case FileOpts.JSON:
                FileConverter._assert_type(object_to_assert=object_to_save, type_to_assert=FileOpts.JSON)
                fullpath = os.path.join(posix_dirname, converted_filename)
                with open(fullpath, "wb") as f:
                    f.write(object_to_save)
            case _:
                raise TypeError(f"Unsupported file type: {ftype}")

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
                    raise TypeError(f"Expected a dict-like object for conversion to JSON. Recieved: {object_to_assert}")
            case _:
                raise TypeError(f"Type assertion called for FileConverter, but an unsupported type was passed: {type_to_assert}")
