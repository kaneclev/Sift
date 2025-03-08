from dataclasses import dataclass
from typing import List

import IR.instructions.operations as ops

from language.parsing.ast.actions.action.action import Action, ActionType
from shared.registry import RegistryType, lookup


@dataclass
class Instruction:
    url: str
    operations: List[ops.operation.Operation]

    @classmethod
    def generate(cls, url: str, action_list: List[Action]):
        new_operation_list: List[ops.operation.Operation] = []
        for action in action_list:
            generator = lookup(rtype=RegistryType.OP, key=action.action_type)
            new_op = generator(action)
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


