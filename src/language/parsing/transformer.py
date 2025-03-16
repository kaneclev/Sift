import logging

from typing import Dict, List, Union

import lark_cython

from lark import Lark, Token, Transformer, exceptions, logger
from lark.tree import Meta

from language.grammar_container import GrammarContainer
from language.parsing.exceptions.external_exception import SyntaxError




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
    ISSUES = {}
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
        context["offense"] = e.token.value
        context["col"] = e.column
        context["line"] = e.line
        expected_rules = e.interactive_parser.choices()
        if not expected_rules:
            raise ValueError(f"There were no valid 'expected next tokens' when an UnexpectedInput error was raised for context: {context}")
        context["expected"] = {}
        for rule in expected_rules:
            if (assoc_value := self.gram_container.get(rule)) is not None:
                context["expected"][rule] = assoc_value
        raise SyntaxError(context=context)
