from typing import List

from IR.ir_base import IntermediateRepresentation
from scraping.sift_requests.target_handler import TargetHandler


class IRTranslator:
    def __init__(self, ir: IntermediateRepresentation):
        self.ir = ir
        self.targ_handlers: List[TargetHandler] = self.translate_targets()
        pass
    def translate_targets(self) -> List[TargetHandler]:
        targ_handlers: List[TargetHandler] = []
        for instr in self.ir:
            targ_handlers.append(TargetHandler(instruction=instr))
        return targ_handlers
