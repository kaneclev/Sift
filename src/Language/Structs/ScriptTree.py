from dataclasses import dataclass
from typing import List, Dict
from Language.Structs.ActionBlock import ActionBlock
from Language.HighLevelStructure.HighLevelTree import HighLevelTree

def parse_action_blocks_to_dataclasses(action_block_list: List[Dict[str, str]]):
    instance_action_block_list = []
    for action_block in action_block_list:
        parsed_block = ActionBlock.generate_action_block(action_block)
        instance_action_block_list.append(parsed_block)
    return instance_action_block_list
@dataclass
class ScriptTree:
    abstract: HighLevelTree
    targets: Dict[str, str]
    action_blocks: List[ActionBlock]
    # Example of a custom "pretty" printing method.
    def __str__(self):
        """
        Return a readable, multiline string representation
        of the ScriptTree and its nested objects.
        """
        lines = []
        lines.append("ScriptTree:")
        lines.append("  Abstract Tree: {}".format(repr(self.abstract)))
        
        # Print Targets
        lines.append("  Targets:")
        for name, url in self.targets.items():
            lines.append(f"    - {name}: {url}")

        # Print Action Blocks
        lines.append("  Action Blocks:")
        for i, block in enumerate(self.action_blocks, start=1):
            lines.append(f"    {i}. {block.pretty_print(indent=6)}")

        return "\n".join(lines)
    @classmethod
    def generate_script_tree(cls, abstract_tree: HighLevelTree):
        abstract = abstract_tree
        targets = abstract_tree.get_all_targets()
        action_blocks = abstract_tree.get_actions()
        instance_action_block_list = parse_action_blocks_to_dataclasses(
            action_block_list=action_blocks
        )
        return cls(
            abstract=abstract, 
            targets=targets, 
            action_blocks=instance_action_block_list
        )