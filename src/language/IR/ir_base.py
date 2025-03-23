from dataclasses import dataclass, field
from typing import List

from language.IR.instructions.instruction import Instruction


@dataclass
class IntermediateRepresentation:
    identifier: str
    instruction_list: List[Instruction] = field(default_factory=list)
    def __str__(self):
        return "\n".join([str(i) for i in self.instruction_list])
    def __repr__(self):
        return str([repr(i) for i in self.instruction_list])
    def __iter__(self):
        return iter(self.instruction_list)
