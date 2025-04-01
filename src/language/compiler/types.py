from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar


class SupportsToDict(Protocol):
    @abstractmethod
    def to_dict(self) -> dict:
        ...

T = TypeVar('T', bound=SupportsToDict)

class Constraint(ABC, Generic[T]):
    ...

class IRNode(ABC):
    @abstractmethod
    def to_dict(self):
        ...