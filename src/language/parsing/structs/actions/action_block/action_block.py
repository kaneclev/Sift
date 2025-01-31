from dataclasses import dataclass
from typing import Dict, List

from language.parsing.structs.actions.action.action import Action
from language.parsing.structs.actions.action_block.action_block_grammar import ActionBlockGrammar
from language.parsing.structs.parsed_node_interface import ParsedNode


@dataclass
class ActionBlock(ParsedNode):
    target: str  # The target alias this block is associated with
    actions: List[Action]  # List of actions performed in this block

    @classmethod
    def generate(cls, target_action_map: Dict[str, str]):
        # ! Interface Implementation
        #   In order to do the above, need to create exceptions for bad cases.
        assert len(target_action_map.keys()) == 1, "More keys given than expected for the factory " \
                                                   f"method of the ActionBlock dataclass: {target_action_map}"
        target, raw_action = next(iter(target_action_map.items()))
        action_block_as_list = ActionBlockGrammar(raw_action).analyze()
        action_list: List[Action] = []
        for action in action_block_as_list:
            action_list.append(Action.generate(content_to_classify=action))
        return cls(target=target, actions=action_list)

    def validate(self) -> bool:
        # ! Interface Implementation
        #TODO
        pass

    def __str__(self):
        # ! Interface Implementation
        # If you want to override __str__ in the same style
        return self.pretty_print(indent=0)

    def pretty_print(self, indent=0) -> str:
        """
        Return a pretty string for the ActionBlock with a given indentation.
        """
        indent_str = " " * indent
        lines = []
        lines.append(f"{indent_str}ActionBlock (target='{self.target}'): ")
        for i, action in enumerate(self.actions, start=1):
            lines.append(f"{indent_str}  {i}. {action.pretty_print(indent=indent + 4)}")
        return "\n".join(lines)

