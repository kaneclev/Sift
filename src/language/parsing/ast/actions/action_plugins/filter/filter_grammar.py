from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

gram_container = GrammarContainer(start="filter_expr")
gram_container.production_map = {
    # Top-level
    "?filter_expr": "or_expr",

    # Keep original left-recursive structure to maintain transformations
    "?or_expr": "and_expr | or_expr \"or\" and_expr -> or_operator",

    "?and_expr": "not_expr | and_expr \"and\" not_expr -> and_operator",

    "?not_expr": "\"not\" not_expr -> not_operator | atom",

    "?atom": "\"(\" filter_expr \")\" -> group | filter_item",

    # Order from most specific to least specific
    "?filter_item": "attribute_filter | tag_filter | text_filter",

    # Original tag_filter preserved
    "tag_filter":
        "\"tag\" WS? (ESCAPED_STRING | options) -> tag",

    # Original attribute_filter preserved
    "attribute_filter":
        "\"attribute\" WS? (pair | \"[\" WS? pair (WS? \",\" WS? pair)* WS? \"]\") -> attribute",

    # Original attribute_value_expr preserved
    "?attribute_value_expr":
        "contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value",

    # Original pair preserved
    "pair":
        "(ESCAPED_STRING | wildcard_value) WS? \":\" WS? "
        "(contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value)",

    # Original text_filter preserved
    "text_filter":
        "\"text\" WS? (contains_text | ESCAPED_STRING | options) -> text",

    # Original rules preserved
    "contains_attribute":
        "\"contains\" WS? (ESCAPED_STRING | options)",

    "contains_text":
        "\"contains\" WS? (ESCAPED_STRING | options)",

    "options":
        "\"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\"",

    "wildcard_value":
        "\"any\""
}


class FilterGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(gram_container, content)
    def analyze(self):
        dict_filter_representation = super().analyze()
        return dict_filter_representation
