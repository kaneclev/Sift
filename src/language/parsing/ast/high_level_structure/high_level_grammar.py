from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

""" The HighLevelGrammar definition using the GrammarContainer class.

The GrammarContainer instance and the associated production_map field
defines the Lark grammar to be interpreted by SyntaxProcessor.
"""
gram_container = GrammarContainer(start="script")
gram_container.production_map = {
    "script": "target_list (action_list)?",
    "target_list": "_TARGETS~1 TL_REGEX_DEFINITION~1",
    "_TARGETS": r"/targets\s*=\s*/",
    "TL_REGEX_DEFINITION": r"/\[[^\]]+\]/",
    "action_list": "action+",
    "action": "target statement_list",
    "target": "SOME_TARGET",
    "SOME_TARGET": r"/[a-zA-Z_^:]+:[\s^\r\n|\r|\n]+/x",
    "statement_list": r"/\{[^\}]*\}/"
}

class HighLevelGrammar(SyntaxProcessor):
    """ Defines an interactor class for HighLevelTree to use.
    Inherits from SyntaxProcessor, who handles the parsing of a given Sift grammar.
    """
    def __init__(self, content):
        """ Initializes the parent SyntaxProcessor for use by HighLevelTree.
        HighLevelTree provides the content-to-parse (sift file content) which
        is then turned into a high-level, mostly raw, intermediate representation
        of the provided Sift script.

        Args:
            content (str): The content of the Sift script file.
        """
        super().__init__(gram_container, content)
