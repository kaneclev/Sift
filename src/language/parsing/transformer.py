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
        # If the key 'data' is a Token, convert it to its string value.
        if isinstance(data, Token):
            data = data.value
        transformed_children = []
        for child in children:
            if isinstance(child, Token):
                transformed_children.append(child.value)
            else:
                transformed_children.append(child)
        # Return a dictionary with the string key.
        return {data: transformed_children}


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
        tree_in_dict_form = transformer.transform(self.parsed_content)
        return tree_in_dict_form
