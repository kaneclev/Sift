import re

from dataclasses import dataclass  # noqa: N999
from typing import Dict, List, Optional, Union

from language.parsing.structs.actions.action.action import Action
from language.parsing.structs.actions.action.action_types import ActionType
from language.parsing.structs.actions.action_plugins.filter.expression_types import (
    LogicalOperatorType,
)
from language.parsing.structs.actions.action_plugins.filter.filter_grammar import (
    FilterGrammar,
)
from language.parsing.structs.actions.action_plugins.filter.filter_types import (
    FilterTypes,
)


@dataclass
class Filter(Action):
    """ 'operator' refers to 'and', 'or', 'not', 'contains' statements within the filter. """
    operator: Optional[LogicalOperatorType] = None
    """ 'filter_type' defines the type of filter this instance applies (tag, attribute, text) """
    filter_type: Optional[FilterTypes] = None
    """ 'value' is the corresponding value associated with the filter type ("div", for example) """
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    """ 'operands' represents nested filter statements within the current statement """
    operands: Optional[List["Filter"]] = None


    def __init__(self, operator=None, filter_type=None, value=None, operands=None):
        super().__init__(
            action_type=ActionType("filter"),
        )
        self.operator: Optional[LogicalOperatorType] = operator
        self.filter_type: Optional[FilterTypes] = filter_type
        self.value: Optional[Union[str, List[str], Dict[str, str]]] = value
        self.operands: Optional[List["Filter"]] = operands

    @classmethod
    def _classify(cls, raw_content: str) -> bool:
        try:
            cls._parse(raw_content)
            return True
        except Exception as e:
            print(f'Classification Error: {e} (in Filter.py)')
            return False

    @classmethod
    def _parse(cls, raw_content: str):
        """ Parses the raw_content string and returns a dictionary representation of the filter.
        Uses the FilterGrammar class to parse the raw_content string.
        Keyword arguments:
        raw_content -- The raw content to be parsed.
        Return: A dictionary representation of the filter.
        """
        instance: "Filter" = cls()
        instance.assign_metadata(raw_content)
        handler: FilterGrammar = FilterGrammar(instance.metadata["raw_filter"])
        content_as_dict: dict = handler.analyze()
        return content_as_dict

    @classmethod
    def generate(cls, raw_content: str) -> "Filter":
        """ Creates an instance of the "Filter" class.

        generate() is the Filter classes' implementation of its parent (Action)'s generate() method.
        It is assumed that before this method is called, the _classify() method has already been called and returned True.

        The generate() method is responsible for creating an instance of the Filter class, and assigning the parsed data to the instance's attributes.

        generate() first calls _parse() on the raw_content, and then uses the parsed data (parsed by FilterGrammar) to build the Filter instance.

        Keyword arguments:
        raw_content -- The content, which has been classified as a Filter, to be parsed and used to build the Filter instance.
        Return: An instance of the Filter class.
        """
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

        parsed_data: str = cls._parse(raw_content)
        return build_filter(parsed_data)

    def assign_metadata(self, raw_content: str) -> None:
        """ Splits the given filter string into parts, and assigns them to the metadata dictionary.

        A helper method for the _parse() method which compiles two regex statements, one for extract-from-where statements and one for extract-where statements.
        Three key-value pairs are inserted into the metadata dictionary: "from_alias", "raw_filter", and "assignment".
            - from_alias is optionally None; this only exists if the filter string is an extract-from-where statement.
                - It should be noted that even if from_alias is None, the key-value pair is still inserted into the dictionary.
            - raw_filter is the component of the filter_string which contains the actual filtering content.
                Terms like "tag", "attribute", "text", and their corresponding values up until the assignment (->) are stored here.
            - assignment is the component of the filter_string which contains the assignment content.
                That is, it contains the alias which the filter stores the filtered data to.

        This method has no return; it only modifies the instance's metadata dictionary.

        The type of the filter_string is mutually exclusive.
        This means that it will either be an extract-from-where statement or an extract-where statement, but not both.

        Keyword arguments:
        raw_content -- The string to be split and assigned to the metadata dictionary.
        Return: None.
        """
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
        extract_from_statement: Union[re.Match, None] = extract_from_where.search(raw_content)
        extract_where_statement: Union[re.Match, None] = extract_where.search(raw_content)

        self.metadata["from_alias"] = ""
        self.metadata["raw_filter"] = ""
        self.metadata["assignment"] = ""

        if extract_from_statement:
            alias: str = extract_from_statement.group(1)
            filt: str = extract_from_statement.group(2)
            assign: str = extract_from_statement.group(3)
            self.metadata["from_alias"] = alias
            self.metadata["raw_filter"] = filt
            self.metadata["assignment"] = assign
        if extract_where_statement:
            filt: str = extract_where_statement.group(1)
            assign: str = extract_where_statement.group(2)
            self.metadata["raw_filter"] = filt
            self.metadata["assignment"] = assign

        return

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
