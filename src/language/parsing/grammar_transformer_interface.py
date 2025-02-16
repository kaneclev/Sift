from typing import Dict

from language.grammar_container import GrammarContainer
from language.parsing.transformer import GrammarHandler


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
