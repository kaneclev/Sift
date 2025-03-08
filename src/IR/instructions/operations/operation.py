from dataclasses import dataclass
from typing import Callable

from language.parsing.ast.actions.action.action import ActionType
from shared.registry import RegistryType, register


@dataclass
class Operation:
    @staticmethod
    def register_op(action_type: ActionType, factory: Callable):
        register(rtype=RegistryType.OP, item=factory, key=action_type)
