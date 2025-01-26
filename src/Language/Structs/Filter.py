from dataclasses import dataclass
from typing import Dict, Optional, List, Union
from Language.Structs.PreciseGrammars.FilterTypes import FilterTypes
from Language.Structs.Action import Action
from Language.Structs.PreciseGrammars.ExpressionTypes import LogicalOperatorType
from Language.Structs.ActionTypes import ActionType
from lark import Lark, logger, Transformer
import logging
@dataclass
class Filter(Action):
    operator: Optional[LogicalOperatorType] = None
    filter_type: Optional[FilterTypes] = None
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    operands: Optional[List["Filter"]] = None

    def __init__(self, operator: Optional[LogicalOperatorType] = None, 
                 filter_type: Optional[FilterTypes] = None, 
                 value: Optional[Union[str, List[str], Dict[str, str]]] = None,
                 operands: Optional[List["Filter"]] = None):
        super().__init__(action_type=ActionType.FILTER_OP, **locals())
        self.operator = operator
        self.filter_type = filter_type
        self.value = value
        self.operands = operands

    def validate(self):
        return super().validate()
    
    def pretty_print(self):
        return super().pretty_print(indent=0)    

    @classmethod
    def generate(cls, filter_content: str):
        """
        Generates a Filter tree from a filter string.

        Args:
            filter_string (str): The filter content to parse (at base-case, this will be a string; 
                recursively, this will be dicts under the 'operands' key which constitute pre-parsed Filter objects)

        Returns:
            Filter: The constructed Filter tree.

        Raises:
            ValueError: If the input data is invalid or cannot be parsed.
        """
        # Parse the string into intermediate data
        if isinstance(filter_content, str):
            data = analyze(filter_string=filter_content)
        else:
            data = filter_content

        # Handle atomic filters with a single value
        if "type" in data and "value" in data:
            return cls(
                filter_type=data["type"],
                value=data["value"]
            )

        # Handle atomic filters with multiple values
        elif "type" in data and "values" in data:
            return cls(
                filter_type=data["type"],
                value=data["values"]  # List or dict of values
            )

        # Handle logical operators with operands
        elif "operator" in data and "operands" in data:
            return cls(
                operator=data["operator"],
                operands=[cls.generate_filter(op) for op in data["operands"]]
            )

        # Handle unexpected data formats
        else:
            raise ValueError(f"Invalid filter data structure: {data}")

    def pretty_print(self, indent=0) -> str:
            super().pretty_print(indent=indent)
            indent_str = " " * indent
            lines = []
            lines.append(f"{indent_str}Filter:")
            lines.append(f"{indent_str}  operator: {self.operator}")
            lines.append(f"{indent_str}  filter_type: {self.filter_type}")
            lines.append(f"{indent_str}  value: {self.value}")
            if self.operands:
                lines.append(f"{indent_str}  operands:")
                for i, operand in enumerate(self.operands, start=1):
                    # Recursively call pretty_print on each operand
                    lines.append(f"{indent_str}    {i}. {operand.pretty_print(indent=indent + 4)}")
            return "\n".join(lines)

    def __str__(self):
        return self.pretty_print(indent=0)
    
    def _draw_tree(self, prefix: str = "", is_tail: bool = True) -> list[str]:
        """
        Internal helper method that returns a list of lines (strings).
        'prefix' is the string used to align branches,
        'is_tail' indicates if this node is the last child of its parent.
        """
        # Describe the current filter node in one line:
        node_label = f"Filter(op={self.operator}, type={self.filter_type}, val={self.value})"

        # '└── ' if it's the last child, otherwise '├── '
        lines = [prefix + ("└── " if is_tail else "├── ") + node_label]

        if self.operands:
            # For all operands except the last, we pass is_tail=False
            # For the last operand, pass is_tail=True
            for i, child in enumerate(self.operands):
                is_last = (i == len(self.operands) - 1)
                # Update the prefix:
                #   If we're the last child, we use "    " (4 spaces)
                #   Otherwise, we use "│   " which maintains the vertical line
                child_prefix = prefix + ("    " if is_tail else "│   ")
                lines.extend(child._draw_tree(child_prefix, is_last))
        return lines

    def draw_tree(self) -> str:
        """
        Public method to return an ASCII-visual representation of this Filter tree.
        """
        return "\n".join(self._draw_tree(prefix="", is_tail=True))

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
      | "text" text_values -> text_filter
      | /text[^\r\n|\r|\n]+contains/x text_values -> contains_text_filter

tag_values: ESCAPED_STRING                       // Single tag
          | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> tag_list // Multiple tags

attribute_values: ESCAPED_STRING
                | ESCAPED_STRING ":" ESCAPED_STRING // Single key-value pair
                | "[" pair ("," pair)* "]" -> attribute_dict // Multiple key-value pairs
text_values: ESCAPED_STRING 
          | "[" ESCAPED_STRING ("," ESCAPED_STRING)* "]" -> text_string_list // Multiple tags

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
            return {"type": FilterTypes.TAG, "values": [val.value for val in tag_values]}  # List of tags
        return {"type": FilterTypes.TAG, "value": tag_values.children[0].value}  # Single tag

    def attribute_filter(self, args):
        print(args)
        attribute_values = args[0]
        if isinstance(attribute_values, dict):
            key_val_attr_dict_list = []
            for attr_key_token, attr_val_token in attribute_values.items():
                curr_attr_key_val_pair = {}
                attr_key, attr_val = attr_key_token.value, attr_val_token.value
                curr_attr_key_val_pair["key"] = attr_key
                curr_attr_key_val_pair["value"] = attr_val
                key_val_attr_dict_list.append(curr_attr_key_val_pair)
            return {"type": FilterTypes.ATTRIBUTE, "values": key_val_attr_dict_list}
            # Then its a list of key-value pairs of attributes.
        if len(attribute_values.children) > 1: # then its a key-pair
            return {"type": FilterTypes.ATTRIBUTE, "key": attribute_values.children[0].value, "value": attribute_values.children[1].value}  # Single key-value pair
        if len(attribute_values.children) == 1:
            return {"type": FilterTypes.ATTRIBUTE, "value": attribute_values.children[0].value} 
        
    def text_filter(self, args):
        text_values = args[0].children
        text_filter_dict = {"type": FilterTypes.TEXT}

        if isinstance(text_values, list):
            if len(text_values) > 1:
                text_filter_dict["values"] = [ val.value for val in text_values ]
            else:
                text_filter_dict["value"] = text_values[0].value
        else:
            raise TypeError(f'Expected the "text" filter to be represented as a list, but it was not: {text_values}')
        return text_filter_dict
    
    def contains_text_filter(self, args):
        text_values = args[1].children[0]
        text_contains_filter_dict = {"type": FilterTypes.TEXT_CONTAINS}

        if isinstance(text_values, list):
            if len(text_values) > 1:
                text_contains_filter_dict["values"] = [ val for val in text_values]
        else:
            text_contains_filter_dict["value"] = text_values
        return text_contains_filter_dict
                
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