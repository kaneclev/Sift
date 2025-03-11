
from dataclasses import asdict
from enum import Enum
from typing import Dict, Union

import orjson

from language.parsing.ast.script_tree import ScriptTree
from shared.utils.file_conversions import FileConverter, FileOpts


class SiftASTConverter(FileConverter):
    """ Utility class for converting a ScriptTree object into different forms. """
    class ConversionOptions(Enum):
        SAVE_FILE = False
        SAVE_LOCATION = "../json_conversions"
    @property
    def default_options(self) -> Dict[ConversionOptions, Union[str, bool]]:
        return {
            SiftASTConverter.ConversionOptions.SAVE_FILE: False,
            SiftASTConverter.ConversionOptions.SAVE_LOCATION: SiftASTConverter.ConversionOptions.SAVE_LOCATION.value
        }
    @staticmethod
    def to_json(ast: ScriptTree, file_name: str, options: Dict[ConversionOptions, Union[str, bool]] = None):
        if not options:
            options = {}
        options = SiftASTConverter.update_options(options_to_update=options, base_options=SiftASTConverter().default_options)
        json_bytes = orjson.dumps(asdict(ast), option=orjson.OPT_INDENT_2)
        to_dir = SiftASTConverter().get_opt(SiftASTConverter.ConversionOptions.SAVE_LOCATION)
        SiftASTConverter._save_as(save_to_dir=to_dir, raw_basename=file_name, ftype=FileOpts.JSON, object_to_save=json_bytes)
        return orjson.loads(json_bytes)

