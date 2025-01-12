from dataclasses import dataclass
from typing import List, Dict
from Language.Structs.Action import Action
from Language.Structs.PreciseGrammars.ActionBlockGrammar import analyze
@dataclass
class ActionBlock:
    target: str  # The target alias this block is associated with
    actions: List[Action]  # List of actions performed in this block
    @classmethod
    def generate_action_block(cls, target_action_map: Dict[str, str]):
        # TODO: need to make error checking; target is defined and is a string, actions is defined and is a string
        #   In order to do the above, need to create exceptions for bad cases.
        assert len(target_action_map.keys()) == 1, "More keys given than expected for the factory" \
                                                   f"method of the ActionBlock dataclass: {target_action_map}"
        target, raw_action = next(iter(target_action_map.items()))
        action_block_as_list = analyze(raw_action)
        action_list: List[Action] = []
        for action in action_block_as_list:
            # TODO 
            pass