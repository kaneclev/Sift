from dataclasses import dataclass
from typing import Dict, List

from language.parsing.high_level_structure.high_level_tree import HighLevelTree
from language.parsing.structs.actions.action_block.action_block import ActionBlock
from language.parsing.structs.parsed_node_interface import ParsedNode


##########################################################
#                  Helper Methods                        #
##########################################################
def parse_action_blocks_to_dataclasses(action_block_list: List[Dict[str, str]]):
    instance_action_block_list = []
    for action_block in action_block_list:
        parsed_block = ActionBlock.generate(action_block)
        instance_action_block_list.append(parsed_block)
    return instance_action_block_list

@dataclass
class ScriptTree(ParsedNode):
    """ Simple representation of the targets defined at the start of the script. """
    targets: Dict[str, str]
    """ The first child of the script tree, containing all the action blocks. """
    action_blocks: List[ActionBlock]



    ##########################################################
    #                  Class Methods                         #
    ##########################################################
    @classmethod
    def generate(cls, abstract_tree: HighLevelTree):
        # ! Interface Implementation
        targets = abstract_tree.get_all_targets()
        action_blocks = abstract_tree.get_actions()
        instance_action_block_list = parse_action_blocks_to_dataclasses(
            action_block_list=action_blocks
        )
        return cls(
            targets=targets,
            action_blocks=instance_action_block_list
        )

    ##########################################################
    #                 Instance Methods                       #
    ##########################################################
    def validate(self) -> bool:
         # ! Interface Implementation
         pass

    def __str__(self):
            # ! Interface Implementation
            """
            Return a readable, multiline string representation
            of the ScriptTree and its nested objects.
            """
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
