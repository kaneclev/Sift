import json

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Dict, Generic, List, Protocol, TypeVar, Union


class SupportsToDict(Protocol):
    @abstractmethod
    def to_dict(self) -> dict:
        ...

T = TypeVar('T', bound=SupportsToDict)

class Constraint(ABC, Generic[T]):
    ...

class LogicalOperator(Enum):
    AND = "and"
    OR = "or"
    NOT = "not"

class ComparisonOperator(Enum):
    EQUALS = "equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    # Easily extended with more operators

class ElementType(Enum):
    TAG = "tag"
    ATTRIBUTE = "attr"
    TEXT = "text"
    # Easily extended with more element types

####################
# Base IR Elements #
####################
class IRJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)
@dataclass(frozen=True)
class IRNode:
    """Base class for all IR nodes"""

    def to_dict(self) -> Dict:
        result = {"type": self.__class__.__name__}
        for key, value in self.__dict__.items():
            if isinstance(value, IRNode):
                result[key] = value.to_dict()
            elif isinstance(value, list) and value and isinstance(value[0], IRNode):
                result[key] = [item.to_dict() for item in value]
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result

    def to_json(self, indent=2) -> str:
        """Convert IR node to a JSON string"""
        return json.dumps(self.to_dict(), indent=indent, cls=IRJSONEncoder)

@dataclass(frozen=True)
class Expression(IRNode):
    """Base class for all expressions"""
    pass

@dataclass(frozen=True)
class Statement(IRNode):
    """Base class for all statements"""
    pass

####################
# Expressions #
####################

@dataclass(frozen=True)
class Literal(Expression):
    """A literal value"""
    value: Any

@dataclass(frozen=True)
class Variable(Expression):
    name: str
    references: Union[Literal, Expression]

@dataclass(frozen=True)
class Target(Variable):
    """Target definition for scraping"""
    references: str
@dataclass(frozen=True)
class Conditional(Expression):
    """A comparison expression (e.g., tag equals "div")"""
    lhs: Expression
    rhs: Expression
    operator: ComparisonOperator

@dataclass(frozen=True)
class LogicalExpression(Expression):
    """A logical combination of expressions"""
    operator: LogicalOperator
    expressions: List[Expression]

####################
# Statements #
####################

@dataclass(frozen=True)
class ExtractStatement(Statement):
    """Statement that extracts elements based on a condition"""
    source: str  # Target name
    condition: Expression
    destination: str  # Variable name



@dataclass(frozen=True)
class Program(IRNode):
    """The complete program"""
    targets: List[Target] = field(default_factory=list)
    statements: List[Statement] = field(default_factory=list)

def ir_to_json(file: str, ir_node: IRNode):
    """Print an IR node as formatted JSON"""
    with open(file, 'w') as f:
        f.write(ir_node.to_json())
