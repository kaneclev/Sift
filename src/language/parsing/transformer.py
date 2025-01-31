import logging

from lark import Lark, Token, Transformer, logger

logger.setLevel(level=logging.DEBUG)

class GenericGrammar(Lark):
    def __init__(self, grammar: str, start: str, content: str):
        super().__init__(grammar, start=start, parser='lalr')
        self.grammar = grammar
        self.content = content
        pass

class GenericTransformer(Transformer):
    def __default__(self, data, children, meta):
        """
        Converts Tree nodes into a nested dictionary structure,
        replacing Token('RULE', ...) with its string value.
        """
        # Convert Tokens to string values
        key = str(data)  # Extract the rule name as a string
        children = [child.value if isinstance(child, Token) else child for child in children]

        # Return as a dictionary with the string name of the rule
        return {key: children if len(children) > 1 else children[0]}

class GrammarHandler:
    """ A Grammar Handler for parsing and transforming a Lark grammar into a dictionary tree.
    Given a grammar, start rule, and content, this class will parse and transform the content into a dictionary tree.

    Methods:
        - parse(): Parses the content using the provided grammar, returning True if the parse was successful and False otherwise
        - transform(): Transforms the parsed content into a dictionary tree
    """
    def __init__(self, grammar: str, start: str, content: str):
        # Define the grammar and content to be parsed
        self.content = content
        self.grammar = grammar
        self.lark_grammar = GenericGrammar(grammar, start, content)
        self.parsed_content = None
    def parse(self) -> bool:
        try:
            self.parsed_content = self.lark_grammar.parse(self.content)
            return True
        except Exception as e:
            # TODO define internal exception for this case
            print(f"Error parsing content: {e}")
            return False
    def transform(self):
        """
        Transforms the parsed content into a dictionary format.
        """
        if self.parsed_content is None:
            print("No parsed content to transform.")
            return None

        transformer = GenericTransformer()
        return transformer.transform(self.parsed_content)
