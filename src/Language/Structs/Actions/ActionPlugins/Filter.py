from dataclasses import dataclass
from typing import Dict, Optional, List, Union
from lark import Lark, logger, Transformer, LarkError
import logging

from Language.Structs.PreciseGrammars.FilterTypes import FilterTypes
from Language.Structs.Actions.Action import Action
from Language.Structs.PreciseGrammars.ExpressionTypes import LogicalOperatorType
from Language.Structs.Actions.ActionTypes import ActionType

logger.setLevel(logging.DEBUG)

@dataclass
class Filter(Action):
    operator: Optional[LogicalOperatorType] = None
    filter_type: Optional[FilterTypes] = None
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    operands: Optional[List["Filter"]] = None

    # Lark grammar definition
    _grammar = Lark(
        r"""
        ?start: expression
        ?expression: or_expression
        ?or_expression: and_expression | or_expression "or" and_expression -> or_expr
        ?and_expression: not_expression | and_expression "and" not_expression -> and_expr
        ?not_expression: primary | "not" primary -> not_expr
        ?primary: filter | "(" expression ")" -> group
        filter: "tag" tag_values -> tag_filter
              | "attribute" attribute_values -> attribute_filter
              | "text" text_values -> text_filter
              | /text[^\r\n|\r|\n]+contains/x text_values -> contains_text_filter
        tag_values: ESCAPED_STRING | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> tag_list
        attribute_values: ESCAPED_STRING | ESCAPED_STRING ":" ESCAPED_STRING 
                        | "[" pair ("," pair)* "]" -> attribute_dict
        text_values: ESCAPED_STRING | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> text_string_list
        pair: ESCAPED_STRING ":" ESCAPED_STRING
        %import common.ESCAPED_STRING
        %import common.WS
        %ignore WS
        """,
        start='start',
        parser='lalr'
    )

    class _Transformer(Transformer):
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
            return {k: v for k, v in args}

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

    def __init__(self, operator=None, filter_type=None, value=None, operands=None):
        super().__init__(
            action_type=ActionType.FILTER_OP,
            operator=operator,
            filter_type=filter_type,
            value=value,
            operands=operands
        )
        self.operator = operator
        self.filter_type = filter_type
        self.value = value
        self.operands = operands

    @classmethod
    def classify(cls, raw_content: str) -> bool:
        try:
            cls._parse(raw_content)
            return True
        except LarkError:
            return False
        except Exception as e:
            logger.debug(f"Classification failed: {str(e)}")
            return False

    @classmethod
    def _parse(cls, filter_string: str):
        ast = cls._grammar.parse(filter_string)
        return cls._Transformer().transform(ast)

    @classmethod
    def _generate(cls, raw_content: str) -> "Filter":
        def build_filter(data):
            if "operator" in data:
                return Filter(
                    operator=data["operator"],
                    operands=[build_filter(op) for op in data["operands"]]
                )
            return Filter(
                filter_type=data["type"],
                value=data.get("value"),
                operands=[build_filter(op) for op in data.get("operands", [])]
            )

        parsed_data = cls._parse(raw_content)
        return build_filter(parsed_data)

    def validate(self):
        if self.operator and not self.operands:
            raise ValueError("Logical operator must have operands")
        if self.filter_type and not self.value:
            raise ValueError("Filter type requires a value")
        if self.operands:
            for operand in self.operands:
                operand.validate()
        return True

    def pretty_print(self, indent=0) -> str:
        indent_str = " " * indent
        lines = [f"{indent_str}Filter({self.operator or ''} {self.filter_type or ''} {self.value or ''})"]
        if self.operands:
            for i, operand in enumerate(self.operands):
                prefix = "└── " if i == len(self.operands)-1 else "├── "
                lines.append(f"{indent_str}{prefix}{operand.pretty_print(indent + 4)}")
        return "\n".join(lines)

    def __repr__(self):
        return self.pretty_print()

    def _draw_tree(self, prefix="", is_tail=True):
        lines = []
        node_repr = f"Filter(op={self.operator}, type={self.filter_type}, val={self.value})"
        lines.append(prefix + ("└── " if is_tail else "├── ") + node_repr)
        if self.operands:
            for i, child in enumerate(self.operands):
                is_last = i == len(self.operands) - 1
                child_prefix = prefix + ("    " if is_tail else "│   ")
                lines.extend(child._draw_tree(child_prefix, is_last))
        return lines

    def draw_tree(self) -> str:
        return "\n".join(self._draw_tree())