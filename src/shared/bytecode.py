from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Union

""" Theory for the Bytecode
~Goals~
- Minimal and Flexbile
- A small generalized set of building blocks that can be combined into more complex operations
- Allows for future expansions on the language without excessive redesign of the opcodes

~First-Design~
Like in compilers course, define dataclasses for the operations/expressions
"""
class PropertyType(Enum):
    TAG = auto()
    TEXT = auto()
    ATTRIBUTE = auto()

class ComparisonQualifier(Enum):
    CONTAINS = auto()

class LogicalOperator(Enum):
    AND = auto()
    NOT = auto()
    OR = auto()
    XOR = auto()

################
## Base ########
################

@dataclass(frozen=True, eq=True)
class Argument:
    ...
@dataclass(frozen=True, eq=True)
class Instruction:
    ...

@dataclass(frozen=True, eq=True)
class SiftProgram:
    instructions: List[Instruction]

##################
## Instructions ##
##################

@dataclass(frozen=True, eq=True)
class Comparison(Instruction):
    op: LogicalOperator
    ...

@dataclass(frozen=True, eq=True)
class Assignment(Instruction):
    arg1: Argument

@dataclass(frozen=True, eq=True)
class HTMLComparison(Comparison):
    arg1: Argument
    arg2: Argument
    op: LogicalOperator
    qualifier: ComparisonQualifier = None


###################
## Arguments ######
###################


@dataclass(frozen=True, eq=True)
class Property(Argument):
    ptype: PropertyType
    definition: Any

@dataclass(frozen=True, eq=True)
class Alias(Argument):
    name: str # The alias in the source code.
    references: Any # The content it references.

###################
## Properties #####
###################


@dataclass(frozen=True, eq=True)
class Tag(Property):
    ptype: PropertyType = PropertyType.TAG
    definition: Union[str, List[str]]

@dataclass(frozen=True, eq=True)
class Attribute(Property):
    ptype: PropertyType = PropertyType.ATTRIBUTE
    definition: Union[Dict[str, str], Dict[str, List[str]]]

@dataclass(frozen=True, eq=True)
class Text(Property):
    ptype: PropertyType = PropertyType.TEXT
    definition: Union[str, List[str]]


