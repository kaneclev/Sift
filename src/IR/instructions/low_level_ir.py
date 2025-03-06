from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Union

from IR.instructions.conditionals import Conditional
from IR.instructions.html_properties import HTMLProperty
from language.parsing.ast.actions.action.action import Action
from language.parsing.ast.actions.action_plugins.filter.filter import Filter
from language.parsing.ast.enums import LogicalOperatorType


class Ops(Enum):
    FILTER = auto()

@dataclass
class Operation(ABC):
    op: Ops
    @classmethod
    def generate(cls, action: Action) -> "Operation":
        op = decide_op(action)
        if op == Ops.FILTER:
            # We know action is a Filter, so cast or confirm:
            if not isinstance(action, Filter):
                raise TypeError("Expected a Filter action for a FILTER op.")
            return FilterIR.generate(filter=action)
        # if you have other Ops, handle them here
        raise NotImplementedError(f"No IR class for type {action}")


@dataclass
class FilterConditional(Conditional):
    constraints: List[Union["FilterConditional", HTMLProperty]]
    def __str__(self, indent: int = 0) -> str:
        indent_str = "    " * indent  # 4 spaces per indent level
        if self.op == LogicalOperatorType.NOT:
            result = f"{indent_str}{self.op.value}\n"
            child = self.constraints[0]
            if isinstance(child, HTMLProperty):
                result += "    " * (indent + 1) + str(child)
            else:
                result += child.to_ir(indent + 1)
            return result

        if len(self.constraints) == 0:
            return ""
        if len(self.constraints) == 1:
            child = self.constraints[0]
            if isinstance(child, HTMLProperty):
                return f"{indent_str}{str(child)}"
            else:
                return child.to_ir(indent)

        first = self.constraints[0]
        if isinstance(first, HTMLProperty):
            output = f"{indent_str}{str(first)}\n"
        else:
            output = first.to_ir(indent) + "\n"

        output += f"{indent_str}{self.op.value}\n\n"

        for cons in self.constraints[1:]:
            if isinstance(cons, HTMLProperty):
                output += f"{'    ' * (indent + 1)}{str(cons)}\n"
            else:
                output += cons.to_ir(indent + 1) + "\n"
        return output.rstrip()

@dataclass
class FilterIR(Operation):
    to_alias: str
    condition: FilterConditional
    from_alias: str = field(default_factory=str)
    @classmethod
    def generate(cls, filter: Filter):
        condition = FilterIR.compose_filters(filter=filter)
        if isinstance(condition, HTMLProperty):
            condition = FilterConditional(op=LogicalOperatorType.ANY, constraints=[condition])
        from_alias = filter.metadata["from_alias"]
        to_alias = filter.metadata["assignment"].replace(';', "")

        return cls(op=Ops.FILTER, condition=condition, to_alias=to_alias, from_alias=from_alias)
    @staticmethod
    def compose_filters(filter: Filter) -> Union[FilterConditional, HTMLProperty]:
        if filter.operator:
            constraints = []
            for op in filter.operands:
                constraints.append(FilterIR.compose_filters(op))
            return FilterConditional(op=filter.operator, constraints=constraints)
        # then its a leaf, base case
        else:
            return HTMLProperty(htype=filter.filter_type, detail=filter.value)

    def __str__(self):
        return f"Filter from {self.from_alias if self.from_alias else '<NA>'} to {self.to_alias} using: \n{str(self.compose_filters())}"



def decide_op(to_decide: Action) -> Ops:
    if to_decide.action_type.plugin_name == "filter":
        return Ops.FILTER
