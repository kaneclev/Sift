from enum import Enum, auto
from typing import List

import orjson

from api.parsing_api.ipc_management.target_handler import TargetHandler
from language.IR.ir_base import IntermediateRepresentation


class RequestServiceFormats(Enum):
    JSON = auto()

##################################
#     RequestManager Format      #
##################################
class RequestServiceFormatter:
    def __init__(self, ir: IntermediateRepresentation):
        self.ir = ir

        self.targ_handlers: List[TargetHandler] = [TargetHandler(instr) for instr in self.ir]
        pass

    def translate(self, format: RequestServiceFormats):
        match format:
            case RequestServiceFormats.JSON:
                return self._json_translation()
            case _:
                raise ValueError(f"Unsupported format to translate to for the RequestService: {format}")

    def _json_translation(self) -> bytes:
        collection = {"targets": []}
        for targ in self.targ_handlers:
            collection["targets"].append(targ.to_dict())
        return orjson.dumps(collection)
