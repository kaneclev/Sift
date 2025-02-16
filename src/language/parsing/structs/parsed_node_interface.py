from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
Node = TypeVar("Node", bound="ParsedNode")  # Generic type bound to ParsedNode

@dataclass
class ParsedNode(ABC, Generic[T]):
    """ An interface for AST nodes to implement for Sift language organization.  
    Offers abstract methods for generating, validating, and providing a human-viewable
    string view of the node.
    """  # noqa: W291

    def to_dict(self):
        """ Implements asdict(), a dataclass method for all classes which inherit from ParsedNode  
        to_dict makes it so that classes which implement ParsedNode do not also have to import
        the dataclasses packages' 'asdict' method.  
        Keyword arguments:  
        None.  
        Return:  (dict) The return value of the dataclasses' asdict() method.
        """  # noqa: W291
        return asdict(self)

    @classmethod
    @abstractmethod
    def generate(cls: Node, data: T) -> Node:
        """ An abstract factory method which all ParsedNode inheritors implement.  
        Given some data, generate() produces an instance of the current class.  
        Keyword arguments:
        data -- any (to be implemented by the child)
        Return: An instance of the current class.
        """  # noqa: W291
        ...

    @abstractmethod
    def validate(self) -> bool:
        """ An instance method for validating the correctness of the structure of an instance of ParsedNode.  
        Keyword arguments:
        None.
        Return: (bool) True if the instance is valid, False otherwise.
        """  # noqa: W291
        ...

    @abstractmethod
    def __str__(self) -> str:
        """ Enforces inclusion of a str method for ParsedNode classes, to encourage human-readable representation.

        Keyword arguments:
        None.
        Return: (str) The human-readable representation of the ParsedNode object.
        """
        ...

