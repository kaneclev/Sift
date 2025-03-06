from enum import Enum


class LogicalOperatorType(Enum):
    OR = 'or'
    AND = 'and'
    NOT = 'not'
    ANY = 'any'


class HTMLPropertyType(Enum):
    TAG = "tag"
    ATTRIBUTE = "attr"
    TEXT = "text"
    UNKNOWN = ""

