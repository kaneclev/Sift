from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

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

hl_grammar = gram_container.to_string()

class HighLevelGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(gram_container, content)
    def analyze(self):
        return super().analyze()
