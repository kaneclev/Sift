from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from language.parsing.ast.actions.action.action import Action
from language.parsing.ast.actions.action.action_types import ActionType
from language.parsing.ast.actions.action_plugins.filter.filter import Filter


class Ops(Enum):
    FILTER = 1

@dataclass
class Operation(ABC):
    op: Ops
    content = None
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
    @abstractmethod
    def to_json(self):
        ...

@dataclass
class FilterIR(Operation):
    @classmethod
    def generate(cls, filter: Filter):
        new_filter = FilterIR(op=Ops.FILTER)
        new_filter.content = filter.to_dict()
        return new_filter
    def to_json(self):
        return ""
def decide_op(to_decide: Action) -> Ops:
    if to_decide.action_type.plugin_name == "filter":
        return Ops.FILTER

