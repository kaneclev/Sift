from dataclasses import dataclass
from typing import Union, List, Dict
from Language.Structs.ActionTypes import ActionType
from Language.Structs.Filter import Filter
@dataclass
class Action:
    action_type: ActionType
    filters: List[Filter]
    @classmethod
    def generate_action(cls, action_string: str):
        # TODO factory method for the Action class.
        #   -> Implements the ActionGrammar parser. 
        pass