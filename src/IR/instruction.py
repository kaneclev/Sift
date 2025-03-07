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
            new_op = Operation.generate(action)
            new_operation_list.append(new_op)
        return Instruction(url=url, operations=new_operation_list)
    def __iter__(self):
        return iter(self.operations)
    def __str__(self):
        ir = [
            f"URL: {self.url}"
        ]
        ir.extend([f"{str(op)}" for op in self.operations])
        return "\n".join(ir)

@dataclass
class IntermediateRepresentation:
    instruction_list: List[Instruction] = field(default_factory=list)
    def __str__(self):
        return "\n".join([i.to_ir() for i in self.instruction_list])
    def __iter__(self):
        return iter(self.instruction_list)
