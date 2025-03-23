import pickle

from dataclasses import asdict
from enum import Enum
from typing import Dict, Union

import orjson

from language.IR.ir_base import IntermediateRepresentation
from shared.utils.file_conversions import FileConverter, FileOpts


class IRConverter(FileConverter):
    class ConversionOptions(Enum):
        SAVE_LOCATION = "../IRConversions"
        SAVE_FILE = True
        DISTINCT_FILENAME = None

    @property
    def default_options(self) -> Dict[ConversionOptions, Union[str, bool]]:
        return {
            IRConverter.ConversionOptions.SAVE_LOCATION: IRConverter.ConversionOptions.SAVE_LOCATION.value
        }

    @staticmethod
    def to_json(ir_obj: IntermediateRepresentation, options: Dict[ConversionOptions, Union[str, bool]] = None) -> None:
        if not options:
            options = {}
        options = IRConverter.update_options(options_to_update=options, base_options=IRConverter().default_options)
        json_bytes = orjson.dumps(asdict(ir_obj))
        to_dir = IRConverter().get_opt(IRConverter.ConversionOptions.SAVE_LOCATION)
        IRConverter.save_as(save_to_dir=to_dir, raw_basename=ir_obj.file_name, ftype=FileOpts.JSON, object_to_save=json_bytes)
    @staticmethod
    def to_pickle(ir_obj: IntermediateRepresentation, options: Dict[ConversionOptions, Union[str, bool]] = None) -> None:
        if not options:
            options = {}
        options = IRConverter.update_options(options_to_update=options, base_options=IRConverter().default_options)
        pkl_bytes = pickle.dumps(asdict(ir_obj))
        if options.get(IRConverter.ConversionOptions.SAVE_FILE) is True:
            file_name = ir_obj.file_name
            if (distinct_file_name := options.get(IRConverter.ConversionOptions.DISTINCT_FILENAME)):
                file_name = distinct_file_name
            to_dir = IRConverter().get_opt(IRConverter.ConversionOptions.SAVE_LOCATION)
            IRConverter.save_as(save_to_dir=to_dir, raw_basename=file_name, ftype=FileOpts.PICKLE, object_to_save=pkl_bytes)
        return pickle.loads(pkl_bytes)
