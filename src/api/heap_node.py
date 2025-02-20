from dataclasses import dataclass


@dataclass(order=True)
class HeapNode:
    priority: int
