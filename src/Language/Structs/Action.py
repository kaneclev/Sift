from dataclasses import dataclass
from Language.Structs.ActionTypes import ActionType
from Language.Structs.PreciseGrammars.ActionGrammar import analyze
from abc import ABC, abstractmethod
from typing import Dict



@dataclass
class Action(ABC):
    _child_registry = []
    action_type: ActionType
    metadata: Dict[str, str]

    def __init__(self, action_type: str, **kwargs):
        self.action_type = action_type
        # Automatically store all keyword arguments as metadata
        self.metadata = {key: value for key, value in kwargs.items()}

    @abstractmethod
    def validate(self):
        ...

    @abstractmethod
    def pretty_print(self, indent=0) -> str:
        ...

    @classmethod
    @abstractmethod
    def generate(cls, **kwargs):
        ...
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Action._child_registry.append(cls)

