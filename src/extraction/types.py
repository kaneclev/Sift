from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Union


class HTMLType(Enum):
    TAG = auto(),
    ATTRIBUTE = auto(), 
    TEXT = auto()
    @staticmethod
    def match(to_match) -> "HTMLType":
        match to_match:
            case 'tag':
                return HTMLType.TAG
            case 'attr':
                return HTMLType.ATTRIBUTE
            case 'text':
                return HTMLType.TEXT
            case _:
                raise TypeError(f"Unexpected HTMLType requested to match: {to_match}")
class ConstraintType(Enum):
    """
    NOTE: The constraint type is actually applicable to the *condition* which contains a series of constraints.
    The constraint itself ought *always* try and match its details; 
    the implications of those matches are determined by the overhead condition.
    
    For example; a condition may have multiple constraints, such that:
    condition: {
        constraint: {
            "htype": "tag",
            "details": [
                "is_contains": True,
                "div"
            ],
        },
        constraint: {
            "htype": "text",
            "details": [
                "is_contains": True,
                "Hi!"
            ],
        }
    }
    """
    MATCH_ANY = auto() # If any of the details in the constraint match, the constraint is satisfied.
    MATCH_ALL = auto() # If *all* of the details in the constraint match, the constraint is satisfied.
    MATCH_NONE = auto() # If *none* of the details in the constraint match, the constraint is satisfied.
    @staticmethod
    def match(to_match) -> "ConstraintType":
        match to_match:
            case 'any': # The optype 'any' imples an OR relationship between all of the details
                return ConstraintType.MATCH_ANY
            case 'and': # The optype 'and' implies an AND relationship between all of the details; all of the details must be satisfied.
                return ConstraintType.MATCH_ALL
            case 'not':
                return ConstraintType.MATCH_NONE
            case _:
                raise TypeError(f"Unexpected ConstraintType requested to match: {to_match}")
@dataclass
class Detail:
    detail: Union[Dict, str, List]
    is_contains: bool
    @staticmethod
    def _handle_nested_dict_detail(value: Dict, detail_object: "Detail", key: str = ""):
        for inner_key, inner_value in value.items():
            if inner_key == "contains":
                #! Then its like {"contains": "..."} or {"contains": [...]}
                detail_object.is_contains = True
                if not isinstance(inner_value, str) and not isinstance(inner_value, list):
                    raise TypeError(f"Unrecognized detail: {inner_key}: {inner_value}")
                if key:
                    detail_object.detail = {key: inner_value}
                    return detail_object
                detail_object.detail = inner_value
                return detail_object
            else:
                if isinstance(inner_value, str):
                    #! Then it must be: {"attr_key": "attr_val"}
                    detail_object.detail = {inner_key: inner_value}
                if isinstance(inner_value, List):
                    #! Then its like {"attr_key": [<attr_val_options>...]}
                    if key:
                        detail_object.detail = {inner_key: inner_value}
                    else:
                        detail_object.detail = inner_value

    @staticmethod
    def read_details(detail_entry: Union[List, Dict]) -> List["Detail"]:
        details: List[Detail] = []
        if isinstance(detail_entry, Dict):
            for key, value in detail_entry.items():
                new_detail: Detail = Detail(None, False)
                if isinstance(value, Dict):
                    new_detail = Detail._handle_nested_dict_detail(value=value, detail_object=new_detail, key=key)
                elif isinstance(value, List):
                    #! Could be: extract where text contains ["i1, i2, i3"]...
                    if key == "contains":
                        new_detail.is_contains = True
                        for inner_value in value:
                            new_detail.detail.append(inner_value)
                    else:
                        new_detail.detail = {key: []}
                        for inner_value in value:
                            new_detail.detail[key].append(inner_value)
                elif isinstance(value, str):
                    if key == "contains":
                        new_detail.is_contains = True
                        new_detail.detail = value
                    else:
                        new_detail.detail = {key: value}
                else:
                    raise TypeError(f"Unexpected type for detail: {key}: {value}")
                details.append(new_detail)
        elif isinstance(detail_entry, List):
            for precise_detail in detail_entry:
                new_detail: Detail = Detail(None, False)
                if isinstance(precise_detail, Dict):
                    #! Then it might be {"contains": [...]} or {"contains": "..."} or {"attr_key": "attr_val"} or {"attr_key": [<attr_val_options>...]}
                    new_detail = Detail._handle_nested_dict_detail(value=precise_detail, detail_object=new_detail)
                elif isinstance(precise_detail, str):
                    new_detail.detail = precise_detail
                #! AND: I think this will never have a list...
                else:
                    raise TypeError(f"Unexpected detail type: {precise_detail} in broader detail context {detail_entry}")
        else:
            raise TypeError(f"Unexpected type for detail entry: {detail_entry}")
        return details




@dataclass
class Constraint:
    htype: HTMLType
    detail: List[Detail]
    constraint_type: 
    @classmethod
    def read_constraint(cls, constraint_dict: Dict) -> "Constraint":
        htype: HTMLType = None
        detail: Detail = None
        for key, val in constraint_dict.items():
            ...
class Constraints:
    def __init__(self, constraints: List[Dict]):
        self.raw = constraints
        self.constraints = self._read_constraints(self.raw)
        pass

    def _read_constraints(self, raw: List[Dict]) -> List[Constraint]:
        for constraint in raw:
            # Iterate through the list of constraints, each of which is a dictionary.
            Constraint.read_constraint(constraint_dict=constraint)

