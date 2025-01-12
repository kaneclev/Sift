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
        abstract = abstract_tree
        targets = abstract_tree.get_all_targets()
        action_blocks = abstract_tree.get_actions()