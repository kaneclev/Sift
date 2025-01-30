from abc import abstractmethod
from dataclasses import dataclass, field  # noqa: N999
from typing import ClassVar, Dict

import language.parsing.exceptions.action_exceptions as act_except

from language.parsing.structs.actions.action.action_types import ActionType
from language.parsing.structs.parsed_node_interface import ParsedNode


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
        super().__init_subclass__(**kwargs)
        Action._child_registry.append(cls)

    @classmethod
    def generate(cls, content_to_classify: str) -> "Action":
        """
        #TODO make docs
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
            return claimed_owners[0].generate(content_to_classify)
    def __str__(self):
        return self.pretty_print()

    @abstractmethod
    def _classify(self, raw_content) -> bool:
        """ Classify; classifies a piece of raw_content as either belonging to this action class or not.
        !-> Part of the Action interface.

        All actions must implement a classify method, which accurately determines whether or not a given string from a Sift
        script can be classified as a member of this particular action.

        For example, if the classify() method is called with raw_content 'extract where tag "div"', the 'ExtractWhere' class ought to return True,
        whereas *all other Action classes must return False*.

        The Action base class will verify that the classify() method only applies to one and only one of its subclasses. If
        there is more than one True return from the list of subclasses, a MultipleActionDefinition exception will be raised from Exceptions  > Internal > ActionExceptions
        Keyword arguments:
        raw_content --  the content to classify as either belonging to this instance or not.
        Return: return_description
        """
        ...


    @abstractmethod
    def pretty_print(self, indent=0) -> str:
        """ A method to print the structure of the Action class in a human-readable way.

        Keyword arguments:
        indent -- The indent to use for structure of the object
        Return: A 'pretty' string view of the object.
        """
        ...
