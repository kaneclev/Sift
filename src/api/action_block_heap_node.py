import heapq

from dataclasses import dataclass, field
from typing import Dict, List

from api.heap_node import HeapNode
from api.target_heap_node import TargetHeapNode


@dataclass
class ActionBlockHeapNode(TargetHeapNode):
    contents: dict
#! NOTE: this needs to take a copy of the targ_heap, not the raw targ_heap
def generate_action_block_heap_node(targ_heap: List[TargetHeapNode], action_blocks: List[Dict]) -> List[ActionBlockHeapNode]:
    action_block_heap = []
    while targ_heap:
        curr_targ = heapq.heappop(targ_heap)
        targ_name = curr_targ.name
        for action_block in action_blocks: # Walk through and find the correct target
            if targ_name == action_block["target"]:
                new_action_block_heap_node = ActionBlockHeapNode(priority=curr_targ.priority, name=curr_targ.name, url=curr_targ.url, contents=action_block)
                heapq.heappush(action_block_heap, new_action_block_heap_node)
    return action_block_heap
