from dataclasses import dataclass, field
from typing import Dict, List


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
