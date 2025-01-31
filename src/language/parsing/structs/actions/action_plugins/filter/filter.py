import logging
import re

from dataclasses import dataclass  # noqa: N999
from typing import Dict, List, Optional, Union

from lark import Lark, LarkError, Transformer, logger

from language.parsing.structs.actions.action.action import Action
from language.parsing.structs.actions.action.action_types import ActionType
from language.parsing.structs.actions.action_plugins.filter.expression_types import (
    LogicalOperatorType,
)
from language.parsing.structs.actions.action_plugins.filter.filter_types import (
    FilterTypes,
)

logger.setLevel(logging.DEBUG)

@dataclass
class Filter(Action):
    operator: Optional[LogicalOperatorType] = None
    filter_type: Optional[FilterTypes] = None
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    operands: Optional[List["Filter"]] = None


    def __init__(self, operator=None, filter_type=None, value=None, operands=None):
        super().__init__(
            action_type=ActionType("filter"),
        )
        self.operator = operator
        self.filter_type = filter_type
        self.value = value
        self.operands = operands

    @classmethod
    def _classify(cls, raw_content: str) -> bool:
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
        instance = cls()
        extract_from_where = re.compile(
            r'''^\s*                 # optional leading whitespace
                extract              # the word "extract"
                \s+                  # at least one space
                from\s+
                (\S+)                # capture the source (e.g., google_news)
                \s+                  # <-- THIS WAS MISSING! Space after the source
                where                # the word "where"
                \s+(.*?)             # capture the condition
                \s*->\s*             # "->" with optional spaces
                (.+?)                # capture the result
                \s*$                 # optional trailing whitespace
            ''',
            re.VERBOSE | re.DOTALL
        )
        extract_from_statement = extract_from_where.search(filter_string)
        instance.metadata["from_alias"] = ""
        instance.metadata["raw_filter"] = ""
        instance.metadata["assignment"] = ""

        if extract_from_statement:
            alias = extract_from_statement.group(1)
            filt = extract_from_statement.group(2)
            assign = extract_from_statement.group(3)
            instance.metadata["from_alias"] = alias
            instance.metadata["raw_filter"] = filt
            instance.metadata["assignment"] = assign
        extract_where = re.compile(
            r'''^\s*                 # optional leading whitespace
                extract              # the word "extract"
                \s+                  # at least one space
                where                # the word "where"
                \s+(.*?)             # capture (lazy) everything up until...
                \s*->\s*            # "->" with optional surrounding spaces
                (.+?)                # capture the rest
                \s*$                 # optional trailing whitespace, then end of string
            ''',
            re.VERBOSE | re.DOTALL
        )


        extract_where_statement = extract_where.search(filter_string)
        if extract_where_statement:
            filt = extract_where_statement.group(1)
            assign = extract_where_statement.group(2)
            instance.metadata["raw_filter"] = filt
            instance.metadata["assignment"] = assign

        ast = instance._grammar.parse(instance.metadata["raw_filter"])
        return instance._Transformer().transform(ast)

    @classmethod
    def generate(cls, raw_content: str) -> "Filter":
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

    def __str__(self):
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
