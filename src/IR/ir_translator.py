from enum import Enum, auto
from typing import List

import orjson

from IR.ir_base import IntermediateRepresentation
from scraping.sift_requests.target_handler import TargetHandler


class RequestServiceFormats(Enum):
    JSON = auto()
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
