from dataclasses import dataclass, field
from typing import Dict, List

from language.exceptions.external_exception import (
    MultipleTargetListDefinitionsError,
)
from language.exceptions.internal_exception import (
    NoRawContentProvidedError,
    TransformerParseError,
)
from language.parsing.ast.actions.action_block import ActionBlock
from language.parsing.grammars import HighLevelGrammar
from language.parsing.utils import ParsedNode


@dataclass
class HighLevelTree(ParsedNode):
    """ Creates an intermediate representation of the Sift file for the ScriptTree class to parse.
    Used by the Parser class. Offers methods for parsing file content into a dict-like half-parsed AST,
    which can then be used to define a more robust, precise AST by the ScriptTree class.
    Args:
        ParsedNode (abstract): The parent class for all AST nodes.

    Raises:
        NoRawContentProvidedError: Raised if there was no content to parse provided.
        TransformerParseError: Raised if HighLevelGrammar returned a malformed high-level AST.
        MultipleTargetListDefinitionsError: Raised if HighLevelGrammar detected multiple 'targets' lists
        TypeError: Raised if there were unexpected types present in the AST.
        ValueError: Raised if there were unexpected values or non-existent expected values in the AST.
        KeyError: Raised if there were expected to be particular keys in the AST dict, but they weren't found.
    """
    parsed_content: Dict
    # ! Expected to be: { "target": "url", }
    targets: Dict[str, str] = field(default_factory=list)
    # ! Expected to be: [ { "target_name", "statement_list"}, ... ]
    actions: List[Dict[str, str]] = field(default_factory=list)

    def __init__(self, parsed_content: Dict):
        """ Takes the resulting AST generated from the HighLevelGrammar class to define the instance.

        The factory method 'generate' uses HighLevelGrammar to create the AST, and the HighLevelTree
        class validates that generated AST.

        Args:
            parsed_content (dict): The AST created by HighLevelGrammar.
        """
        self.AST = parsed_content
        self.validate()

    @classmethod
    def generate(cls, file_contents: str):
        """ Given the raw sift file contents, generates an instance of HighLevelTree.

        Provides HighLevelGrammar with the file contents before calling analyze() to get the
        AST. Returns an instance of HighLevelTree, constructed using the AST.

        Args:
            file_contents (str): The entire raw contents of the Sift file

        Returns:
            HighLevelTree: The corresponding generated instance.
        """
        parsed_content = HighLevelGrammar(file_contents).analyze()
        return cls(parsed_content=parsed_content)

    def validate(self) -> None:
        """ Validates the correctness of the generated AST.
        Raises an exception if the AST is malformed for any reason.
        Returns:
            None.
        """
        script_values_list = []
        mapped_members_to_validate = {
            "targets_mapping": None,
            "actions_list": []
        }
        # check to make sure SiftFile actually parsed something from the file.
        if not self.AST:
            raise NoRawContentProvidedError()
        # check to make sure the 'script' key exists, denoting the list of elements that the HighLevelGrammar parsed.
        if (script_values_list := self.AST.get("script", None)) is None:
            raise TransformerParseError("validate()", f"The dict-representation of the file here: \
                                        {self.AST} does not contain the 'script' key as expected.")
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
            raise ValueError(f"Validation failed for the 'actions' field for HighLevelTree. Parsed Content: {self.AST}")
        if not mapped_members_to_validate["targets_mapping"]:
            raise ValueError(f"Validation failed for the 'targets' field for HighLevelTree. Parsed Content: {self.AST}")

        # Otherwise, everything is a-okay, and we can assign the mapped content to our own members
        self.targets = mapped_members_to_validate["targets_mapping"]
        self.actions = mapped_members_to_validate["actions_list"]

    def parse_targets_definitions(self, target_definitions_string: str) -> Dict[str, str]:
        """ Parses the target list definition from the AST.

        Given the raw representation of the targets list provided by self.AST,
        transforms the string into a dict representation, so that it can be assigned to
        self.targets.

        Args:
            target_definitions_string (str): self.AST's interpretation of the 'targets'
                                            list definition in the Sift file.

        Returns:
            dict[str, str]: The targets list such that { 'targ_name': 'url', ... }
        """
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

    def parse_action_list(self, action_list: List[Dict[str, List[Dict[str, List]]]]) -> List[Dict[str, List]]:
        """ Parses the action_list value from self.AST into a more concise form.
        Given the self.AST's interpretation of the list of actions, expected to be:
        [

            {

            'action': [ {'target': ['Amazon: ']}, {'statement_list': [ ... ]}]

            }

        ]

        parse_action_list transforms this interpretation to the form:

        [

            {

                'target': [ <statement_list> ]

            }

        ]

        Args:
            action_list (List[Dict[str, List[Dict[str, List]]]]): The raw action list interpretation by self.AST.

        Raises:
            TypeError: Raised if the types of structures in action_list are unexpeccted.
            ValueError: Raised if the action_list is missing key-pair values expected to be present in the action_list.

        Returns:
            List[Dict[str, List]]: The more concise, interpretable representation to be assigned to self.actions.
        """
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

    def parse_action(self, action: List[Dict[str, List]]) -> Dict[str, List]:
        """ Parses a single 'action' from the AST into a more simple form.
        *Helper method for parse_action_list*

        Given an 'action' generated by self.AST of the form:
        [
            {
                'target': ['Amazon: ']
            },
            {
                'statement_list': [ ... ]
            }
        ]

        parse_action transforms this into the form:
        {
            'targ_name': [ <statement list> ]
        }
        Raises:
            TypeError: Raised if any of the entries in 'action' are not dicts as expected.
            KeyError: Raised if any of the entries in action do not have the expected key-value pairs.
        Returns:
            Dict[str, List[str]]: The transformed, simpler action.
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
        """ __str__ method required to be implemented by base class """
        pass


@dataclass
class ScriptTree(ParsedNode):
    """ The root node of the tree representation of a Sift script.  
    *#! Implements the ParsedNode interface.*
    """  # noqa: W291

    targets: Dict[str, str]
    """ Simple representation of the targets defined at the start of the script. """
    action_blocks: List[ActionBlock]
    """ The first child of the script tree, containing all the action blocks. """


    @classmethod
    def generate(cls, abstract_tree: HighLevelTree):
        """
        # TODO (docstring)
        """
        targets = abstract_tree.targets
        action_blocks = abstract_tree.actions
        instance_action_block_list = []

        for action_block in action_blocks:
            parsed_block = ActionBlock.generate(action_block)
            instance_action_block_list.append(parsed_block)

        return cls(
            targets=targets,
            action_blocks=instance_action_block_list
        )

    def validate(self) -> bool:
        """ Validates that the necessary components for the ScriptTree class are present after construction.

        The only requirement for the ScriptTree currently follows the requirements outlined for the Sift language.
        It is acceptable if there are no ActionBlocks defined yet; however, at least a list of Targets are expected.

        Returns:
            bool: True if the instance passes validation, False otherwise.
        """
        if not self.targets:
            # While we will accept an empty ActionBlocks list, we cannot accept an empty targets list.
            return False
        return True

    def __str__(self):
        lines = []
        lines.append("ScriptTree:")

        # Print Targets
        lines.append("  Targets:")
        for name, url in self.targets.items():
            lines.append(f"    - {name}: {url}")

        # Print Action Blocks
        lines.append("  Action Blocks:")
        for i, block in enumerate(self.action_blocks, start=1):
            lines.append(f"    {i}. {block.pretty_print(indent=6)}")

        return "\n".join(lines)
