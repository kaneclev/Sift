from dataclasses import dataclass, field
from typing import List, Union

from IR.instructions.conditionals import Conditional
from IR.instructions.html_properties import HTMLProperty
from IR.instructions.operations.operation import Operation
from language.parsing.ast.actions.action.action import ActionType
from language.parsing.ast.actions.action_plugins.filter.filter import Filter
from language.parsing.ast.enums import LogicalOperatorType


@dataclass
class FilterConditional(Conditional):
    constraints: List[Union["FilterConditional", HTMLProperty]]
    def to_ir(self, indent: int = 0) -> str:
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
    optype: str = field(default_factory=str)
    @classmethod
    def generate(cls, filter: Filter):
        condition = FilterIR.compose_filters(filter=filter)
        if isinstance(condition, HTMLProperty):
            condition = FilterConditional(op=LogicalOperatorType.ANY, constraints=[condition])
        from_alias = filter.metadata["from_alias"]
        to_alias = filter.metadata["assignment"].replace(';', "")
        return cls(condition=condition, to_alias=to_alias, from_alias=from_alias)
    def __post_init__(self):
        if self.from_alias:
            self.optype = "FilterOp_ExtractFromWhere"
        else:
            self.optype = "FilterOp_ExtractWhere"
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
        return f"Filter from {self.from_alias if self.from_alias else '<NA>'} to {self.to_alias} using: \n{str(self.condition.to_ir())}"
    def __repr__(self):
        return f"FilterIR (from: {self.from_alias or '<NA>'}, to {self.to_alias}, cond: {self.condition})"

Operation.register_op(action_type=ActionType("filter"), factory=FilterIR.generate)
