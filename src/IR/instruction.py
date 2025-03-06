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
        exit()
        return Instruction(url=url, operations=new_operation_list)

    def to_ir(self):
        ir = [
            f"URL: {self.url}"
        ]
        ir.extend([f"{op.to_ir()}" for op in self.operations])
        return "\n".join(ir)

@dataclass
class IntermediateRepresentation:
    instruction_list: List[Instruction] = field(default_factory=list)
    def __post_init__(self):
        self.IR_STRING = "\n".join([i.to_ir() for i in self.instruction_list])
