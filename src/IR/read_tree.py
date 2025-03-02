from typing import Dict, List

from IR.instruction import Instruction, IntermediateRepresentation
from IR.instructions.low_level_ir import Operation, Ops
from language.parsing.ast.actions.action.action import Action
from language.parsing.ast.parsed_node_interface import ParsedNode
from language.parsing.ast.script_tree import ScriptTree

# Each IR node is going to be an ActionBlock.

class TreeReader:
    @staticmethod
    def ast_to_instructions(ast: ScriptTree) -> Dict[str, Dict]:
        instructions = IntermediateRepresentation()
        # sort the action blocks
        action_blocks = TreeReader._get_ordered_action_blocks(targets=ast.targets, action_blocks=ast.action_blocks)
        # collect all the actions from the sorted list of action blocks
        url_action_list_dict = TreeReader._action_blocks_to_actions(action_blocks=action_blocks, targets=ast.targets)
        instructions_object_list = TreeReader._actions_to_instructions(url_action_dict=url_action_list_dict)
        print(instructions_object_list)    
    @staticmethod
    def _actions_to_instructions(url_action_dict: Dict[str, List[Action]]) -> List[Instruction]:
        instr_list: List[Instruction] = []
        for url, action_list in url_action_dict.items():
            new_instruction = Instruction.generate(url=url, action_list=action_list)
            instr_list.append(new_instruction)
        return instr_list

    @staticmethod
    def _action_blocks_to_actions(action_blocks, targets) -> Dict[str, List[Action]]:
        first_abstraction_ir = {}
        for block in action_blocks:
            first_abstraction_ir[targets[block.target]] = block.actions
        return first_abstraction_ir
    @staticmethod
    def _get_ordered_action_blocks(targets, action_blocks) -> List:
        action_block_order_map = {target: idx for idx, target in enumerate(targets)}
        return sorted(action_blocks, key=lambda block: action_block_order_map.get(block.target, float('inf')))
