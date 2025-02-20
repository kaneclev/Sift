import heapq

from dataclasses import dataclass

from api.heap_node import HeapNode


@dataclass
class TargetHeapNode(HeapNode):
    name: str
    url: str

def generate_target_heap_nodes(target_map: dict):
    targ_node_list = []
    targ_p = 0
    for targ, url in target_map.items():
        new_node = TargetHeapNode(priority=targ_p, name=targ, url=url)
        heapq.heappush(targ_node_list, new_node)
        targ_p += 1
    return targ_node_list
