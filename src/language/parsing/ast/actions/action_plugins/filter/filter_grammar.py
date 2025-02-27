from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

gram_container = GrammarContainer(start="filter_expr")
gram_container.production_map = {
    "?filter_expr": "or_expr",
    "?or_expr": "and_expr | or_expr \"or\" and_expr -> or_operator",
    "?and_expr": "not_expr | and_expr \"and\" not_expr -> and_operator",
    "?not_expr": "\"not\" not_expr -> not_operator | atom",
    "?atom": "\"(\" filter_expr \")\" -> group | filter_item",
    "?filter_item": "tag_filter | attribute_filter | text_filter",
    "tag_filter": "\"tag\" WS? (ESCAPED_STRING | \"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\") -> tag",
    "attribute_filter": "\"attribute\" WS? (ESCAPED_STRING (WS? \":\" WS? attribute_value_expr)? | \"[\" WS? pair (WS? \",\" WS? pair)* WS? \"]\") -> attribute",
    "?attribute_value_expr": "\"contains\" WS? (ESCAPED_STRING | \"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\") -> contains_attribute | ESCAPED_STRING",
    "pair": "ESCAPED_STRING WS? \":\" WS? attribute_value_expr",
    "contains_text": "\"contains\" WS? (ESCAPED_STRING | \"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\")",
    "text_filter": "\"text\" WS? (contains_text | ESCAPED_STRING | \"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\") -> text"
}
class FilterGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(gram_container, content)
    def analyze(self):
        dict_filter_representation = super().analyze()
        return dict_filter_representation
