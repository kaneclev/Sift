from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
Node = TypeVar("Node", bound="ParsedNode")  # Generic type bound to ParsedNode

@dataclass
class ParsedNode(ABC, Generic[T]):
    @classmethod
    @abstractmethod
    def generate(cls: Node, data: T) -> Node:
        ...

    @abstractmethod
    def validate(self) -> bool:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

