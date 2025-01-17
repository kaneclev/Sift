import re
from copy import deepcopy
import json

from Language.HighLevelStructure.HighLevelGrammar import analyze
import Language.Exceptions.InternalException as ITE


class HighLevelTree:
    def __init__(self, file_contents: str):
        self.tree: dict = analyze(file_contents)
        self._validate_tree_structure()
        self._discern_targets()
        self._discern_statement_lists_in_action_list()
        pass

    def _discern_targets(self):
        # Get target list as a string
        target_list_string: str = self.tree.get("target_list")

        # Remove list syntax if present
        target_list_string = target_list_string.strip("[]")
        
        # Split pairs by comma into a list
        target_pairs: list = target_list_string.split(',')
        
        # Create the dictionary to hold parsed key-value pairs
        new_targets_as_dict = {}
        
        for pair in target_pairs:
            # Clean up the string: remove whitespace, quotes, and backslashes
            pair = re.sub(r'[\\"]', '', pair).strip()
            
            # Split into key-value pair (assuming valid input)
            key, value = map(str.strip, pair.split(':', 1))

            # Add to dictionary
            new_targets_as_dict[key] = value
        
        # Update the tree with the parsed dictionary
        self.tree["target_list"] = new_targets_as_dict


    def _discern_statement_lists_in_action_list(self):
    # Fetch the action_list once for better performance
        action_list = self.tree.get("action_list")
        
        for i in range(len(action_list)):  # Iterate over the entire list
            entry = action_list[i]  # Fetch the current entry
            if isinstance(entry, dict):
                # Create a new entry dictionary
                new_entry = {}
                
                # Validate and clean the target
                target = entry.get("target")
                if target is None or not isinstance(target, str):
                    raise ITE.TransformerParseError(
                        "action()",
                        f"Action item in action_list does not have a 'target' *string* property as expected: {entry}"
                    )
                target = re.sub(r'[:]', '', target).strip()
                
                # Validate the statement list
                statement_list_for_target = entry.get("statement_list")
                if statement_list_for_target is None or not isinstance(statement_list_for_target, str):
                    raise ITE.TransformerParseError(
                        "statement_list()",
                        f"Statement list associated with target {target} is either non-existent or not a string: {entry}"
                    )
                
                # Add the cleaned target and statement_list to the new entry
                new_entry[target] = statement_list_for_target
                
                # Update the action_list in place
                action_list[i] = new_entry
            else:
                raise ITE.TransformerParseError(
                    "action_list()",
                    f"Action list does not contain dicts as expected: {action_list}"
                )

    
    def get_actions(self) -> list:
        return self.tree.get("action_list", []) 
    
    def get_all_targets(self) -> dict:
        return self.tree.get("target_list")

    def get_target(self, target_var_or_url) -> str | None:
        targ_list = self.get_all_targets()
        if targ_list.get(target_var_or_url, None) is None:
            for var, url in targ_list.items():
                if url == target_var_or_url:
                    return {var: url}
        else:
            return {target_var_or_url: targ_list.get(target_var_or_url)}

    def get_statement_list_by_target(self, target):
        action_list = self.tree.get("action_list")
        if action_list:
            for entry in action_list:
                if entry.get(target, None) is not None:
                    return {target: entry[target]}

    def _validate_tree_structure(self): 
        # Performs a second validation on the structure, ensuring all keys are there and that absolute requirements (i.e., an existent and valid target list) are present
        if not isinstance(self.tree, dict):
            raise ITE.TransformerParseError("script()", "HLTransformer did not return a 'dict' type after parsing the Sift file.")
        targets_string = self.tree.get("target_list", None)
        if targets_string is None:
            raise ITE.HighLevelTreeParseError(method="_validate_tree_structure()", 
                                              reason="No targets list key found; Grammar was expected to validate this.")
        action_list = self.tree.get("action_list", None)
        if action_list is None:
            self.tree["action_list"] = []
        return

    def print_tree(self):
        print(json.dumps(self.tree, indent=4))
        return json.dumps(self.tree, indent=4)
    def get_tree(self):
        return deepcopy(self.tree)
    

