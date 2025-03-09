from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

gram_container = GrammarContainer(start="filter_expr")
gram_container.production_map = {
    # Top-level
    "?filter_expr": "or_expr",

    "?or_expr": "and_expr | or_expr \"or\" and_expr -> or_operator",

    "?and_expr": "not_expr | and_expr \"and\" not_expr -> and_operator",

    "?not_expr": "\"not\" not_expr -> not_operator | atom",

    "?atom": "\"(\" filter_expr \")\" -> group | filter_item",

    "?filter_item": "tag_filter | attribute_filter | text_filter",

    # Example: "tag" plus either a single ESCAPED_STRING or options
    "tag_filter":
        "\"tag\" WS? (ESCAPED_STRING | options) -> tag",

    # "attribute" plus either a single pair or bracketed pairs
    "attribute_filter":
        "\"attribute\" WS? (pair | \"[\" WS? pair (WS? \",\" WS? pair)* WS? \"]\") -> attribute",

    # The attribute_value_expr can be:
    #  (1) contains_attribute,
    #  (2) options,
    #  (3) ESCAPED_STRING,
    #  (4) wildcard_value ("any")
    "?attribute_value_expr":
        "contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value",

    # pair (key: value)
    "pair":
        "(ESCAPED_STRING | wildcard_value) WS? \":\" WS? "
        "(contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value)",

    # "text" plus either contains_text, an ESCAPED_STRING, or options
    "text_filter":
        "\"text\" WS? (contains_text | ESCAPED_STRING | options) -> text",

    # ---- Defined rules so Lark won't complain "used but not defined"
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
