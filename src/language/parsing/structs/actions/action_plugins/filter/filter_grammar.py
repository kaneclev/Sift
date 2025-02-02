from lark import Transformer

from language.parsing.grammar_transformer_interface import SyntaxProcessor
from language.parsing.structs.actions.action_plugins.filter.expression_types import (
    LogicalOperatorType,
)
from language.parsing.structs.actions.action_plugins.filter.filter_types import (
    FilterTypes,
)

grammar = """
        ?start: expression

        ?expression: or_expression

        ?or_expression: and_expression
                    | or_expression "or" and_expression -> operator

        ?and_expression: not_expression
                        | and_expression "and" not_expression -> operator

        ?not_expression: primary
                        | "not" primary -> operator


        ?primary: type
                | "(" expression ")" -> group

        type: "tag" tag -> tag
            | "attribute" attribute -> attribute
            | "text" text -> text
            | /text[^\r\n|\r|\n]+contains/x text -> contains_text

        tag: ESCAPED_STRING                       // Single tag
                | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> tag_list // Multiple tags

        attribute: ESCAPED_STRING
                        | ESCAPED_STRING ":" ESCAPED_STRING // Single key-value pair
                        | "[" pair ("," pair)* "]" -> attribute_dict // Multiple key-value pairs
        text: ESCAPED_STRING
                | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> text_string_list // Multiple tags

        pair: ESCAPED_STRING ":" ESCAPED_STRING  // Key-value pair

        %import common.ESCAPED_STRING  // Handles quoted strings like "div"
        %import common.WS
        %ignore WS

        """

class FilterTransformer(Transformer):
    # TODO Update Transformer such that we dont have any tree or token objects. below is a sample of what we see currently for lengthy_sample
    """
    """
    def tag_filter(self, args):
        tag_values = args[0]
        if isinstance(tag_values, list):
            return {"type": FilterTypes.TAG, "values": [str(v) for v in tag_values]}
        return {"type": FilterTypes.TAG, "value": str(tag_values)}

    def attribute_filter(self, args):
        attr_values = args[0]
        if isinstance(attr_values, dict):
            return {"type": FilterTypes.ATTRIBUTE, "values": attr_values}
        if isinstance(attr_values, list) and len(attr_values) == 2:
            return {"type": FilterTypes.ATTRIBUTE, "key": str(attr_values[0]), "value": str(attr_values[1])}
        return {"type": FilterTypes.ATTRIBUTE, "value": str(attr_values)}

    def text_filter(self, args):
        text_values = args[0]
        if isinstance(text_values, list):
            return {"type": FilterTypes.TEXT, "values": [str(v) for v in text_values]}
        return {"type": FilterTypes.TEXT, "value": str(text_values)}

    def contains_text_filter(self, args):
        text_values = args[0]
        if isinstance(text_values, list):
            return {"type": FilterTypes.TEXT_CONTAINS, "values": [str(v) for v in text_values]}
        return {"type": FilterTypes.TEXT_CONTAINS, "value": str(text_values)}

    def tag_list(self, args):
        return [str(v) for v in args]

    def attribute_dict(self, args):
        return dict(args)

    def text_string_list(self, args):
        return [str(v) for v in args]

    def pair(self, args):
        return (str(args[0]), str(args[1]))

    def and_expr(self, args):
        return {"operator": LogicalOperatorType.AND, "operands": args}

    def or_expr(self, args):
        return {"operator": LogicalOperatorType.OR, "operands": args}

    def not_expr(self, args):
        return {"operator": LogicalOperatorType.NOT, "operands": args}

    def group(self, args):
        return args[0]


class FilterGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(grammar, 'start', content)
    def analyze(self):
        dict_filter_representation = super().analyze()
        new_k_v_pair = {}

        for key, value in dict_filter_representation.items():
            match key:
                case "tag":
                    new_k_v_pair["type"] = FilterTypes.TAG
                case _:
                    pass
            # Values will be in dict format
            for val_key, val_val in value.items():

                match val_key:
                    case "tag_list":
                        new_k_v_pair["values"] = [str(v) for v in val_val]
                    case _:
                        pass
        print(new_k_v_pair)
        return new_k_v_pair
