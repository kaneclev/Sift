

from dataclasses import dataclass, field
from typing import Dict, List

from language.parsing.exceptions.external_exception import (
    MultipleTargetListDefinitionsError,
)
from language.parsing.exceptions.internal_exception import (
    NoRawContentProvidedError,
    TransformerParseError,
)
from language.parsing.high_level_structure.high_level_grammar import HighLevelGrammar
from language.parsing.structs.parsed_node_interface import ParsedNode


@dataclass
class HighLevelTree(ParsedNode):
    parsed_content: Dict
    # ! Expected to be: { "target": "url", }
    targets: Dict[str, str] = field(default_factory=list)
    # ! Expected to be: [ { "target_name", "statement_list"}, ... ]
    actions: List[Dict[str, str]] = field(default_factory=list)

    def __init__(self, parsed_content: str):
        self.parsed_content = parsed_content
        self.validate()

    @classmethod
    def generate(cls, file_contents: str):

        parsed_content = HighLevelGrammar(file_contents).analyze()
        return cls(parsed_content=parsed_content)

    def validate(self):
        script_values_list = []
        mapped_members_to_validate = {
            "targets_mapping": None,
            "actions_list": []
        }
        # check to make sure SiftFile actually parsed something from the file.
        if not self.parsed_content:
            raise NoRawContentProvidedError()
        # check to make sure the 'script' key exists, denoting the list of elements that the HighLevelGrammar parsed.
        if (script_values_list := self.parsed_content.get("script", None)) is None:
            raise TransformerParseError("validate()", f"The dict-representation of the file here: \
                                        {self.parsed_content} does not contain the 'script' key as expected.")
        for script_element in script_values_list:
            # Now we are going to walk through the key value pairs and populate our memeber variables (targets, actions)
            if isinstance(script_element, dict):
                # ! Target List
                if (target_list := script_element.get("target_list", None)) is not None:
                    if len(target_list) > 1: # There should only be one element in the target list; that element is the entire targets: [] list.
                        original_definition = target_list[0]
                        alternate_definitions = target_list[1:]
                        # Raise exception if there are multiple definitions.
                        raise MultipleTargetListDefinitionsError(original_definition=original_definition,
                                                                 offending_alternate_definitions=alternate_definitions)
                    # Otherwise, map this 'feature' of the script to the content map.
                    mapped_members_to_validate["targets_mapping"] = self.parse_targets_definitions(target_list[0])
                # ! Action Definitions Container
                if (action_list := script_element.get("action_list", None)) is not None:
                    if not isinstance(action_list, list):
                        raise TypeError(f"'action_list' in the HighLevelGrammar parsed dict is \
                                        expected to be a list, but instead was {action_list}")
                    mapped_members_to_validate["actions_list"] = self.parse_action_list(action_list)

        # Final validation for the map.
        if not mapped_members_to_validate["actions_list"]:
            raise ValueError(f"Validation failed for the 'actions' field for HighLevelTree. Parsed Content: {self.parsed_content}")
        if not mapped_members_to_validate["targets_mapping"]:
            raise ValueError(f"Validation failed for the 'targets' field for HighLevelTree. Parsed Content: {self.parsed_content}")

        # Otherwise, everything is a-okay, and we can assign the mapped content to our own members
        self.targets = mapped_members_to_validate["targets_mapping"]
        self.actions = mapped_members_to_validate["actions_list"]
        return True

    def parse_targets_definitions(self, target_definitions_string: str):
        no_brackets = target_definitions_string.replace('[', "").replace(']', "")
        no_newlines = no_brackets.replace("\n", "")
        no_spaces = no_newlines.replace(" ", "")
        split_by_comma: list[str] = no_spaces.split(',')
        targets_dict =  {}
        for pair in split_by_comma:
            split_pair = pair.split(":", 1)
            key = split_pair[0]
            val = split_pair[1].replace('"', "")
            targets_dict[key] = val
        return targets_dict

    def parse_action_list(self, action_list: list) -> list:
        parsed_action_list = []
        for action_dict in action_list:
            if not isinstance(action_dict, dict):
                raise TypeError(f"The 'action_list' list containing the dict action entries here: {action_list} \
                was expected to strictly contain elements of type 'dict', but contained otherwise (here: {action_dict})")
            if (action_contents := action_dict.get("action", None)) is None:
                raise ValueError(f"Key confusion; expected the key 'action' in the current dict: \
                                 {action_dict} in the context: {action_list}")
            parsed_action_list.append(self.parse_action(action_contents))
        return parsed_action_list

    def parse_action(self, action: list) -> dict:
        """
        all elements in the nested 'action' value list inside an action_list element should be a dict
        example 'action' value:
            {'action': [{'target': ['Amazon: ']}, {'statement_list': [ ... ]}] }
        """
        if any(not isinstance(attribute, dict) for attribute in action):
            raise TypeError(f"The 'action' list containing the target and the statement list here: {action} \
                            was expected to strictly contain elements of type 'dict', but contained otherwise ")
        if (target_raw := action[0].get("target", None)) is None:
            raise KeyError(f"Expected the 'target' field to be present in the 'action' dict here: {action}")
        if (stmt_list := action[1].get("statement_list", None)) is None:
            raise KeyError(f"Expected the 'statement_list' field to be present in the 'action' dict here: {action}")
        # The target value first appears as a list, so move that.
        target_raw = target_raw[0]
        # The statement list first appears as a list, so move that (its just a container with one long string)
        stmt_list = stmt_list[0]
        cleaned_target = target_raw.replace(" ", "").replace(":", "")
        action_entry_dict = {cleaned_target: stmt_list}
        return action_entry_dict

    def __str__(self):
        pass






