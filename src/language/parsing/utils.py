import logging

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Dict, Generic, List, TypeVar, Union

import lark_cython

from lark import Lark, Token, Transformer, exceptions, logger
from lark.tree import Meta

#!#########################
#!## INTERFACES ###########
#!#########################
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


#!#########################
#!## GRAMMAR UTIITIES #####
#!#########################
@dataclass
class GrammarContainer:
    """ Dataclass for creation of Lark grammars.

    ### How to create a GrammarContainer:
        - Define an instance of GrammarContainer with the starting
        production rule (as a string) in the constructor
        - Define the instance's production_map, where each key is
        the name of the production rule and the associated value is the Lark-style
        syntax for the production rule
            -- *Note*: No colons are necessary in the string between the production rule
            name and the associated parsing syntax grammar.

    ### What you DON'T need in your grammar dict:
        - Comment ignoring statements
        - WS Imports
        - Escaped String Imports
    ### What the GrammarContainer class offers:
        - A consistent way to represent all Sift grammars.
        - A to_string method that will include all the common imports
        and represent the grammar in the typical 'lark' style.
        - A dataclass which is compatible with SyntaxProcessor, used to parse
        raw Sift script text.

    """
    start: str = None
    production_map: Dict[str, str] = field(default_factory=dict)
    parser: str = field(default="lalr")

    _comment_identifier = "COMMENTS: /\\/\\/[^\r\n|\r|\n]+/x"
    _imports = [
        r"%import common.WS",
        r"%ignore WS",
        r"%ignore COMMENTS",
        r"%import common.ESCAPED_STRING"
    ]

    def to_string(self) -> str:
        """ A method to transform the GrammarContainer dataclass into a Lark-parsable string grammar.
        Uses the class's member 'production_map' to generate the grammar before adding on typical imports,
        like comment ignores or Common imports.
        Returns:
            str: The Lark-parsable string representation of the grammar.
        """
        grammar_list: List[str] = []
        for rule_name, production_definition in self.production_map.items():
            grammar_list.append(": ".join([rule_name, production_definition]))
        grammar_list.append(self._comment_identifier)
        for imp in self._imports:
            grammar_list.append(imp)
        # Finally, join them separated by newlines.
        return "\n".join(grammar_list)

    def get(self, rule: str):
        if (found := self.production_map.get(rule, None)) is not None:
            return found
        # then see if there is a qualifier before the key that we could still mathc
        for rule_name, value in self.production_map.items():
            print(f"Found rule: {rule_name} in map with value: {value}")
            if rule_name[1:] == rule or rule_name[:-1] == rule:
                return value

class SyntaxProcessor:
    """ A base class for Grammar classes to inherit from.

    When a Grammar class implements the SyntaxProcessor, this base class handles the interface
    between GrammarContainer, GrammarHandler, and the actual Grammar implementation class.
    """
    def __init__(self, grammar: GrammarContainer, content: str):
        """ Given a GrammarContainer and the raw content to be parsed, provides an instance of SyntaxProcessor.

        A Grammar class creates an instance of GrammarContainer when defining the parse grammar for their functionality.

        By inheriting from SyntaxProcessor, a child's constructor need not know the details of the creation
        of the GrammarHandler class, nor the interaction between GrammarHandler and the grammar they defined in their
        GrammarContainer instance.

        Args:
            grammar (GrammarContainer): A populated GrammarContainer instance.
            content (str): The raw string script content to be parsed by SyntaxProcessor.
        """
        self.grammar = grammar
        self.start = self.grammar.start
        self.content = content
        self.handler = GrammarHandler(grammar, self.start, content)
        pass
    def analyze(self) -> Dict:
        """ The API for parsing raw script content into an intermediate object.

        Uses the GrammarHandler class to parse and transform string content from a Sift script
        into a dictionary structure, which can then be used to generate a real class instance
        for the action associated with the grammar.

        If the handler cannot parse the content, a GrammarHandlerError exception is raised.

        Returns:
            Dict: The dictionary representation of the parse tree if no exception was raised.
        """
        return self.handler.transform()

# A logger used by Lark in reporting any information related to the content parsing
logger.setLevel(level=logging.INFO)
class GenericGrammar(Lark):
    """ A base class for abstracting Lark instance creation.

    *Note:* This class is not indended to be used outside of transformer.py

    *Inherits from Lark*
    """
    def __init__(self, grammar: str, start: str, content: str):
        """ Initializes the parent Lark instance with some universal settings.

        The purpose of GenericGrammar is to help us avoid re-defining a Lark object over and over,
        specifying the same settings each time.

        Using GenericGrammar, we can avoid this by only requiring the varying information to be passed to us;
        that is, the grammar we will use, the starting rule, and the content we will parse.

        GenericGrammar will specify the parser and the cache-setting automatically on construction, and will store the grammar
        and the content to be parsed.

        Args:
            grammar (str): The *string* representation of the grammar to be passed to Lark.
            start (str): The starting rule as a string to be passed to Lark.
            content (str): The Sift script content that Lark will ultimately parse.
        """
        super().__init__(grammar, start=start, parser='lalr', cache=True, _plugins=lark_cython.plugins)
        self.grammar = grammar
        self.content = content
        pass

class GenericTransformer(Transformer):
    """ A base class for interfacing with the Lark 'Transformer' class.

    *Note:* This class is not indended to be used outside of transformer.py

    Args:
        Transformer (Lark.Transformer): Inherits from Lark's 'Transfomer' class,
            which aids in generating a dict-like object from a Lark 'Tree' instance.
    """
    def __default__(self, data: Union[Token, str], children: List[Union[Token, Dict[str, List[str]]]], meta: Meta):
        """ Overrides the Lark.Transformer 'default' method for transforming a Lark.Tree node.

        The parameters passed are passed by Lark during the 'Transformation' stage of the parsing.

        Args:
            data (Union[Token, str]): The token (or string name of the production rule) for the current node.
            children (List[Union[Token, Dict[str, List[str]]]]): The children of the Node, as either a Token instance,
                or an already-transformed dictionary of values.
            meta (Meta): Line information and other meta-info for the parsed content.
                (https://lark-parser.readthedocs.io/en/stable/classes.html#lark.Tree)

        Returns:
            dict: The dictionary representation of the Lark parse tree.
        """
        # If the key 'data' is a Token, convert it to its string value.
        if isinstance(data, Token):
            data = data.value
        transformed_children = []
        for child in children:
            if isinstance(child, lark_cython.Token):
                transformed_children.append(child.value)
            else:
                transformed_children.append(child)
        # Return a dictionary with the string key.
        return {data: transformed_children}


class GrammarHandler:
    """ A Grammar Handler for parsing and transforming a Lark grammar into a dictionary tree.

    Given a grammar, start rule, and content, this class will parse and transform the content into a dictionary tree.

    *Note:* This is strictly intended to be implemented by SyntaxProcessor.
    """
    def __init__(self, grammar: GrammarContainer, start: str, content: str):
        """ Creates a GrammarHandler using a GrammarContainer instance, the start rule, and the content to be parsed.

        Given a GrammarContainer instance which contains the definition for the grammar,
        we use the GrammarContainer's 'to_string' instance method to put the grammar into lark-readable form.
        GrammarHandler then owns an instance of the GenericGrammar class, which can be used as a Lark instance.

        To start, the 'parsed_content' member variable holds None until GrammarHandler's 'parse' method is called.
        Args:
            grammar (GrammarContainer): The GrammarContainer provided by SyntaxProcessor.
            start (str): The starting rule (which must be defined in the GrammarContainer.)
            content (str): The raw content which will be parsed with the grammar.
        """
        # Define the grammar and content to be parsed
        self.content = content
        self.gram_container = grammar
        self.grammar = grammar.to_string()
        self.lark_grammar = GenericGrammar(self.grammar, start, content)
        self.parsed_content = None

    def parse(self) -> None:
        """ Parses the content using the grammar provided, but does not transform it.

        Raises a GrammarHandlerError if there was an issue parsing.

        Raises:
            GrammarHandlerError: The exception raised by Lark at the time of parsing.
        """
        self.parsed_content = self.lark_grammar.parse(self.content, on_error=self.handle_unexpected_token)
    def transform(self) -> Dict:
        """ Transforms the content parsed by Lark into a dictionary format.

        Returns:
            dict: The transformed parsed content.
        """
        if not self.parsed_content:
            self.parse()

        transformer = GenericTransformer()
        tree_in_dict_form = transformer.transform(self.parsed_content)
        return tree_in_dict_form

    def handle_unexpected_token(self, e: exceptions.UnexpectedInput):
        context = {}


        context["offense"] = e.get_context(self.content)
        context["col"] = e.column
        context["line"] = e.line
        expected_rules = e.interactive_parser.choices()
        context["expected"] =expected_rules
        if not expected_rules:
            raise ValueError(f"There were no valid 'expected next tokens' when an UnexpectedInput error was raised for context: {context}")
        raise SyntaxError(context=context)

