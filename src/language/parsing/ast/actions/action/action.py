from abc import abstractmethod
from dataclasses import dataclass, field  # noqa: N999
from typing import ClassVar, Dict

import language.parsing.exceptions.internal_exception as act_except

from language.parsing.ast.actions.action.action_types import ActionType
from language.parsing.ast.parsed_node_interface import ParsedNode


@dataclass
class Action(ParsedNode):
    """ The base class which all Action classes inherit from.

    This class handles the registration and construction of all sub-action classes.
    Use the generate method with any string to get an instance of the Action class the string corresponds to.
    """
    _child_registry: ClassVar[list["Action"]] = []

    action_type: ActionType
    metadata: Dict[str, str] = field(default_factory=dict)

    def __init_subclass__(cls, **kwargs):
        """
        Initialize a subclass of Action and register it in the child registry.

        Keyword arguments:
        kwargs -- Additional keyword arguments.
        """
        super().__init_subclass__(**kwargs)
        Action._child_registry.append(cls)

    @classmethod
    def generate(cls, content_to_classify: str) -> "Action":
        """
        Generate an Action instance based on the content to classify.

        This method iterates through all registered subclasses of Action and uses their _classify method to determine
        which subclass the content belongs to. If more than one subclass claims the content, a MultipleActionDefinitionsError
        is raised. If no subclass claims the content, a NoDefinitionFoundError is raised.

        Keyword arguments:
        content_to_classify -- The content to classify and generate an Action instance for.

        Returns:
        An instance of the appropriate Action subclass.
        """
        claimed_owners: list["Action"] = []
        for action_subclass in Action._child_registry:
            if action_subclass._classify(content_to_classify) is True:
                claimed_owners.append(action_subclass)
        if len(claimed_owners) > 1:
            raise act_except.MultipleActionDefinitionsError(claimed_owners)
        elif len(claimed_owners) == 0:
            raise act_except.NoDefinitionFoundError(content_to_classify)
        else:
            generated_obj = claimed_owners[0].generate(content_to_classify)
            return generated_obj

    def __str__(self):
        """
        Return a pretty-printed string representation of the Action instance.

        Returns:
        A human-readable string representation of the Action instance.
        """
        return self.pretty_print()

    @abstractmethod
    def _classify(self, raw_content) -> bool:
        """
        Classify a piece of raw_content as either belonging to this action class or not.

        All actions must implement a classify method, which accurately determines whether or not a given string from a Sift
        script can be classified as a member of this particular action.

        Keyword arguments:
        raw_content -- The content to classify as either belonging to this instance or not.

        Returns:
        A boolean indicating whether the content belongs to this action class.
        """
        ...

    @abstractmethod
    def pretty_print(self, indent=0) -> str:
        """
        Print the structure of the Action class in a human-readable way.

        Keyword arguments:
        indent -- The indentation level for pretty-printing (default is 0).

        Returns:
        A human-readable string representation of the Action class structure.
        """
        ...
