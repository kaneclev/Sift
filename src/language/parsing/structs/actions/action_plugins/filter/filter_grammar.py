from language.parsing.grammar_transformer_interface import SyntaxProcessor

grammar = r"""
// Top-level: the filter expression is the starting rule.
?filter_expr: or_expr

// Logical operators
?or_expr: and_expr
        | or_expr "or" and_expr    -> or_operator

?and_expr: not_expr
         | and_expr "and" not_expr -> and_operator

?not_expr: "not" not_expr          -> not_operator
         | atom

?atom: "(" filter_expr ")"         -> group
     | filter_item

// Atomic filter items (flattened so that the subrule names are not in the output)
?filter_item: tag_filter
            | attribute_filter
            | text_filter

// Tag filter: inlined so that the output is directly the value(s)
tag_filter: "tag" WS? (ESCAPED_STRING
                      | "[" WS? ESCAPED_STRING (WS? "," WS? ESCAPED_STRING)* WS? "]") -> tag

attribute_filter: "attribute" WS? (ESCAPED_STRING (WS? ":" WS? attribute_value_expr)?
                      | "[" WS? pair (WS? "," WS? pair)* WS? "]") -> attribute

// This rule handles the value portion of an attribute filter.
// It either allows for the "contains" operator followed by a string (or list of strings),
// or just a plain ESCAPED_STRING.
?attribute_value_expr: "contains" WS? (ESCAPED_STRING
                      | "[" WS? ESCAPED_STRING (WS? "," WS? ESCAPED_STRING)* WS? "]") -> contains_attribute
                      | ESCAPED_STRING


pair: ESCAPED_STRING WS? ":" WS? attribute_value_expr

// Text filter: supports a plain text value, a list of values, or the 'contains' keyword
?contains_text: "contains" WS? (ESCAPED_STRING
                | "[" WS? ESCAPED_STRING (WS? "," WS? ESCAPED_STRING)* WS? "]")

text_filter: "text" WS? (contains_text
                | ESCAPED_STRING
                | "[" WS? ESCAPED_STRING (WS? "," WS? ESCAPED_STRING)* WS? "]") -> text
// Import common tokens
%import common.ESCAPED_STRING
%import common.WS // whitespace
%ignore WS
"""
class FilterGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(grammar, 'filter_expr', content)
    def analyze(self):
        dict_filter_representation = super().analyze()
        return dict_filter_representation
