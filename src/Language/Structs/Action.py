from dataclasses import dataclass
from typing import Union, List, Dict
from Language.Structs.ActionTypes import ActionType
from Language.Structs.Filter import Filter
from Language.Structs.PreciseGrammars.ActionGrammar import analyze
import json
@dataclass
class Action:
    action_type: ActionType
    filters: List[Filter]
    @classmethod
    def generate_action(cls, action_string: str):
        analyzed = analyze(string_content_to_analyze=action_string)
        print(json.dumps(analyzed, indent=4))
        pass