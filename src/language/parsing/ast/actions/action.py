from abc import abstractmethod
from dataclasses import dataclass, field  # noqa: N999
from typing import Dict

import language.exceptions.internal_exception as act_except

from language.parsing.utils import ParsedNode


@dataclass
class ActionType:
    plugin_name: str
    def __eq__(self, value):
        return self.plugin_name == value
    def __init__(self, name: str):
        self.plugin_name = name
    def __hash__(self):
        return hash(self.plugin_name)
    def __repr__(self):
        return self.plugin_name
    def __str__(self):
        return self.plugin_name


@dataclass
class Action(ParsedNode):
    """ The base class which all Action classes inherit from.

    This class handles the registration and construction of all sub-action classes.
    Use the generate method with any string to get an instance of the Action class the string corresponds to.
    """

    action_type: ActionType
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def unfit_content(cls):
        raise act_except.IncorrectContentForPluginError(plugin=cls.__class__.__name__)

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
