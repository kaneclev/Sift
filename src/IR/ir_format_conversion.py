from dataclasses import asdict
from enum import Enum
from typing import Dict, Union

import orjson

from IR.ir_base import IntermediateRepresentation
from shared.utils.file_conversions import FileConverter, FileOpts


class IRConverter(FileConverter):
    class ConversionOptions(Enum):
        SAVE_LOCATION = "../IRConversions"

    @property
    def default_options(self) -> Dict[ConversionOptions, Union[str, bool]]:
        return {
            IRConverter.ConversionOptions.SAVE_LOCATION: IRConverter.ConversionOptions.SAVE_LOCATION.value
        }

    @staticmethod
    def to_json(ir_obj: IntermediateRepresentation, options: Dict[ConversionOptions, Union[str, bool]] = None):
        if not options:
            options = {}
        options = IRConverter.update_options(options_to_update=options, base_options=IRConverter().default_options)
        json_bytes = orjson.dumps(asdict(ir_obj))
        to_dir = IRConverter().get_opt(IRConverter.ConversionOptions.SAVE_LOCATION)
        IRConverter._save_as(save_to_dir=to_dir, raw_basename=ir_obj.file_name, ftype=FileOpts.JSON, object_to_save=json_bytes)
        return orjson.loads(json_bytes)


