from dataclasses import dataclass, field
from typing import Callable, Dict, Generic, List, Tuple, TypeVar, Union

from language.parsing.ast.actions.action import Action, ActionType
from language.parsing.ast.actions.action_plugins.filter.filter import Filter
from language.parsing.ast.enums import HTMLPropertyType, LogicalOperatorType
from language.parsing.ast.trees import ScriptTree
from shared.registry import RegistryType, lookup, register

#! Constraint can be anything; this is where the flexibility comes in.
#! Future implementations of filters can have different *kinds* of conditionals by allowing for varying constraints
Constraint = TypeVar("Constraint")

############################
### Factory Class For IR ###
############################
class IntermediateConstructor:
    @staticmethod
    def to_ir(AST: ScriptTree, identifier: str) -> "IntermediateRepresentation":  # noqa: N803
        ir = IntermediateConstructor.ast_to_instructions(AST, identifier=identifier)
        return ir

    @staticmethod
    def ast_to_instructions(AST: ScriptTree, identifier: str) -> "IntermediateRepresentation":  # noqa: N803
        # sort the action blocks
        action_blocks = IntermediateConstructor._get_ordered_action_blocks(targets=AST.targets, action_blocks=AST.action_blocks)
        # collect all the actions from the sorted list of action blocks
        url_action_list_dict = IntermediateConstructor._action_blocks_to_actions(action_blocks=action_blocks, targets=AST.targets)
        instructions_object_list = IntermediateConstructor._actions_to_instructions(url_action_dict=url_action_list_dict)
        return IntermediateRepresentation(identifier=identifier, instruction_list=instructions_object_list)

    @staticmethod
    def _actions_to_instructions(url_action_dict: Dict[str, List[Action]]) -> List["Instruction"]:
        instr_list: List[Instruction] = []
        for url, action_tuple in url_action_dict.items():
            new_instruction = Instruction.generate(url=url, alias=action_tuple[1], action_list=action_tuple[0])
            instr_list.append(new_instruction)
        return instr_list

    @staticmethod
    def _action_blocks_to_actions(action_blocks, targets) -> Dict[str, List[Tuple[Action, str]]]:
        first_abstraction_ir = {}
        for block in action_blocks:
            first_abstraction_ir[targets[block.target]] = (block.actions, block.target)
        return first_abstraction_ir

    @staticmethod
    def _get_ordered_action_blocks(targets, action_blocks) -> List:
        action_block_order_map = {target: idx for idx, target in enumerate(targets)}
        return sorted(action_blocks, key=lambda block: action_block_order_map.get(block.target, float('inf')))

###########################
### IR Internal Objects ###
###########################
@dataclass
class IntermediateRepresentation:
    identifier: str
    instruction_list: List["Instruction"] = field(default_factory=list)
    def __str__(self):
        return "\n".join([str(i) for i in self.instruction_list])
    def __repr__(self):
        return str([repr(i) for i in self.instruction_list])
    def __iter__(self):
        return iter(self.instruction_list)

@dataclass
class Conditional(Generic[Constraint]):
    op: LogicalOperatorType
    constraints: List[Union["Conditional", Constraint]] = field(default_factory=[])

@dataclass
class Operation:
    @staticmethod
    def register_op(action_type: ActionType, factory: Callable):
        register(rtype=RegistryType.OP, item=factory, key=action_type)

@dataclass
class HTMLProperty:
    htype: HTMLPropertyType
    detail: Union[str, List, Dict]
    def __str__(self):
        return f'{self.htype.value} {self.detail}'

@dataclass
class Instruction:
    url: str
    alias: str
    operations: List[Operation]

    @classmethod
    def generate(cls, url: str, alias: str, action_list: List[Action]):
        new_operation_list: List[Operation] = []
        for action in action_list:
            generator = lookup(rtype=RegistryType.OP, key=action.action_type)
            new_op = generator(action)
            new_operation_list.append(new_op)
        return Instruction(url=url, alias=alias, operations=new_operation_list)

    def __iter__(self):
        return iter(self.operations)

    def __str__(self):
        ir = [
            f"URL: {self.url}"
        ]
        ir.extend([f"{str(op)}" for op in self.operations])
        return "\n".join(ir)
    def __repr__(self):
        return str([repr(op) for op in self.operations])

#######################
### IR Object Types ###
#######################

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
