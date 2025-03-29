from dataclasses import dataclass, field
from typing import Generic, List, TypeVar, Union

from language.parsing.ast.enums import LogicalOperatorType

Constraint = TypeVar("Constraint")

@dataclass
class Conditional(Generic[Constraint]):
    op: LogicalOperatorType
    constraints: List[Union["Conditional", Constraint]] = field(default_factory=[])



