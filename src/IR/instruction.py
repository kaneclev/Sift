from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List

from IR.instructions.low_level_ir import Operation
from language.parsing.ast.actions.action.action import Action


@dataclass
class Instruction:
    url: str
    operations: List[Operation]
    @classmethod
    def generate(cls, url: str, action_list: List[Action]):
        new_operation_list: List[Operation] = []
        for action in action_list:
            new_operation_list.append(Operation.generate(action))
        return Instruction(url=url, operations=new_operation_list)

    @abstractmethod
    def to_json(self):
        self.json = {"url": self.url, "operations": [op.to_json() for op in self.operations]}

@dataclass
class IntermediateRepresentation:
    instruction_list: List[Instruction] = field(default_factory=list)
