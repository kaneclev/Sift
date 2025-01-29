from dataclasses import dataclass, field  # noqa: N999
from language.structs.actions.action_types import ActionType
import language.structs.exceptions.internal.action_exceptions as act_except
from abc import ABC, abstractmethod
from typing import Dict, final, ClassVar
@dataclass
class Action(ABC):
    """ The base class which all Action classes inherit from.

    This class handles the registration and construction of all sub-action classes.
    Use the generate_action method with any string to get an instance of the Action class the string corresponds to.
    """
    _child_registry: ClassVar[list["Action"]] = []

    action_type: ActionType
    metadata: Dict[str, str] = field(default_factory=dict)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Action._child_registry.append(cls)

    @classmethod
    @final
    def generate_action(cls, content_to_classify: str) -> "Action":
        """ Returns an Action instance for the given string statement
        If there are multiple subclasses which claim the statement, a MultipleActionDefinitions exception is raised.
        If there are no subclasses which claim the statement, a NoDefinitionFound exception is raised.

        Otherwise, an instance of the Action subclass which claims the statement is returned.

        Keyword arguments:
        argument -- description
        Return: return_description
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
            return claimed_owners[0]._generate(content_to_classify)

    @abstractmethod
    def _validate(self):
        """ # TODO A method to validate the structure of a created Action object
        """
        ...

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

    @classmethod
    @abstractmethod
    def _generate(cls, raw_content: str) -> "Action":
        """ Factory method for subclasses of the Action base class.

        Keyword arguments:
        raw_content -- the string to pass to the subclass factory method.
        Return: An instance of the action subclass.
        """
        ...

