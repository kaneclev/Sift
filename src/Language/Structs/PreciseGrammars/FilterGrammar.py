from Language.Structs.PreciseGrammars.ExpressionTypes import LogicalOperatorType
from Language.Structs.PreciseGrammars.FilterTypes import FilterTypes
from lark import Lark, logger, Transformer
import logging
logger.setLevel(level=logging.DEBUG)

filter_grammar = """
?start: expression

?expression: or_expression

?or_expression: and_expression
               | or_expression "or" and_expression -> or_expr

?and_expression: not_expression
                | and_expression "and" not_expression -> and_expr

?not_expression: primary
                | "not" primary -> not_expr

?primary: filter
        | "(" expression ")" -> group

filter: "tag" tag_values -> tag_filter
      | "attribute" attribute_values -> attribute_filter

tag_values: ESCAPED_STRING                         // Single tag
          | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> tag_list // Multiple tags

attribute_values: ESCAPED_STRING ":" ESCAPED_STRING  // Single key-value pair
                | "{" pair ("," pair)* "}" -> attribute_dict // Multiple key-value pairs

pair: ESCAPED_STRING ":" ESCAPED_STRING  // Key-value pair

%import common.ESCAPED_STRING  // Handles quoted strings like "div"
%import common.WS
%ignore WS

"""
class FilterGrammar(Lark):
    def __init__(self, filter: str):
        super().__init__(filter_grammar, start='start', parser='lalr')
        self.contents = filter
    def parse(self):
        return super().parse(self.contents)

class FilterTransformer(Transformer):
    def tag_filter(self, args):
        tag_values = args[0]
        if isinstance(tag_values, list):
            return {"type": FilterTypes.TAG, "values": tag_values}  # List of tags
        return {"type": FilterTypes.TAG, "value": tag_values}  # Single tag

    def attribute_filter(self, args):
        attribute_values = args[0]
        if isinstance(attribute_values, dict):
            return {"type": FilterTypes.ATTRIBUTE, "values": attribute_values}  # Dict of attributes
        return {"type": FilterTypes.ATTRIBUTE, "key": attribute_values[0], "value": attribute_values[1]}  # Single key-value pair

    def tag_list(self, args):
        return args  # List of tags

    def attribute_dict(self, args):
        return dict(args)  # Convert list of pairs to a dictionary

    def pair(self, args):
        return args[0], args[1]  # Return a tuple (key, value)

    def and_expr(self, args):
        return {"operator": LogicalOperatorType.AND, "operands": args}

    def or_expr(self, args):
        return {"operator": LogicalOperatorType.OR, "operands": args}

    def not_expr(self, args):
        return {"operator": LogicalOperatorType.NOT, "operands": [args[0]]}

    def group(self, args):
        return args[0]  # Return grouped expression directly

def analyze(filter_string: str):
    ast = FilterGrammar(filter=filter_string).parse()
    return FilterTransformer().transform(ast)