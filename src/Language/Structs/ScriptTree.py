from dataclasses import dataclass, field
from typing import List, Dict, Union, Optional
from Language.Structs.ActionBlock import ActionBlock
from Language.HighLevelStructure.HighLevelTree import HighLevelTree

@dataclass
class ScriptTree:
    abstract: HighLevelTree
    targets: Dict[str, str]
    action_blocks: List[ActionBlock]

    @classmethod
    def generate_script_tree(cls, abstract_tree: HighLevelTree):
        abstract = abstract_tree # No more manipulation needed
        targets = abstract_tree.get_all_targets() # No more manipulation needed
        print(f'calling get_actions')
        action_blocks = abstract_tree.get_actions() # Second-order grammar; these action blocks contains more diverse kinds of statements
        ScriptTree.parse_action_blocks_to_dataclasses(action_block_list=action_blocks)    
    @classmethod 
    def parse_action_blocks_to_dataclasses(cls, action_block_list: List[Dict[str, str]]):
        for action_block in action_block_list:
            parsed_block = ActionBlock.generate_action_block(action_block)