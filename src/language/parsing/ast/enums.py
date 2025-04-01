from enum import Enum
import json
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

class LogicalOperatorType(Enum):
    OR = 'or'
    AND = 'and'
    NOT = 'not'
    ANY = 'any'



def match_logical_op_type(op_str: str) -> LogicalOperatorType:
    if op_str == 'or':
        return LogicalOperatorType.OR
    elif op_str == 'and':
        return LogicalOperatorType.AND
    elif op_str == 'not':
        return LogicalOperatorType.NOT
    else:
        raise ValueError(f"Invalid logical operator type: {op_str}")


class HTMLPropertyType(Enum):
    TAG = "tag"
    ATTRIBUTE = "attr"
    TEXT = "text"
    UNKNOWN = "Unknown"

