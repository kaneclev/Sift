from typing import Dict, Union

from language.parsing.transformer import GrammarHandler


class SyntaxProcessor:
    def __init__(self, grammar, start, content):
        self.grammar = grammar
        self.start = start
        self.content = content
        self.handler = GrammarHandler(grammar, start, content)
        pass
    def analyze(self) -> Union[Dict, None]:
        if self.handler.parse(): # Parses the parent class's grammar, which is then stored as a member var.
            # This will make the parent transform its previously parsed content into a dict.
            return self.handler.transform()
        return None
