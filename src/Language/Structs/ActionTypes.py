from enum import Enum
from dataclasses import dataclass, field

@dataclass
class ActionType:
    extract_type: str = field(default_factory=str)
    assignment: str = field(default_factory=str)
    @classmethod
    def define_action_type(cls, filter_keyword_dict: dict):
        action_type = ActionType()
        for k, v in filter_keyword_dict.values():
            if k == "type":
                if v == "extract_from":
                    action_type.extract_type = "ExtractFrom"
                if v == "extract_where":
                    action_type.extract_type = "ExtractWhere"
            if k == "label":
                action_type.assignment = v
        if action_type.extract_type == "ExtractFrom" and not action_type.assignment:
            # TODO: need to raise the appropriate exception. if the script says 'extract from' but doesnt reference a previously defined variable to extract from then its bad
            pass
        
