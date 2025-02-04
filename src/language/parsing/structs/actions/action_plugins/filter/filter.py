"""
This module defines a `Filter` class, which represents a parsed filtering action
within a custom domain-specific language (DSL). The `Filter` class is part of a
larger parsing framework that deals with statements of the form:

    extract from {some_source} where {some_condition} -> {some_alias}
    extract where {some_condition} -> {some_alias}

The `Filter` itself is organized around logical operators (`and`, `or`, `not`) 
and atomic filtering structures (tag, attribute, text), along with nested 
operands. The methods in this file handle:

1. Parsing the raw filter expressions into a structured `Filter` object
   hierarchy (via `_parse`, `_build_filter`, etc.).
2. Providing utilities to traverse or serialize the `Filter` tree 
   (`traverse`, `pretty_print`, `draw_tree`, etc.).
3. Storing metadata that may arise from the DSL's grammar (via `assign_metadata`).
4. Validating that constructed filter trees conform to expected rules.

Example usage:

    # Suppose we have a DSL statement:
    raw_statement = "extract from google_news where (tag='div' and attribute='main') -> result"

    # We can parse and generate a Filter object:
    f = Filter.generate(raw_statement)

    # Then we can validate it:
    f.validate()

    # And inspect its structure:
    print(f.pretty_print())
    print(f.draw_tree())

"""

import re
from dataclasses import dataclass  # noqa: N999
from typing import Dict, Iterator, List, Optional, Union

from language.parsing.structs.actions.action.action import Action
from language.parsing.structs.actions.action.action_types import ActionType
from language.parsing.structs.actions.action_plugins.filter.expression_types import (
    LogicalOperatorType,
    match_logical_op_type,
)
from language.parsing.structs.actions.action_plugins.filter.filter_grammar import (
    FilterGrammar,
)
from language.parsing.structs.actions.action_plugins.filter.filter_types import (
    FilterTypes,
    match_filter_type,
)


@dataclass
class Filter(Action):
    """
    Represents a filtering action within the DSL. A `Filter` can be either:

    - An atomic filter (e.g., filtering by tag, attribute, or text).
    - A logical operator (e.g., `and`, `or`, `not`) combining one or more operands.
    - A "group" node that contains another filter expression in parentheses.

    Attributes:
        operator (Optional[LogicalOperatorType]):
            The logical operator if this filter is an operator node (e.g. `and`, `or`, `not`).
        filter_type (Optional[FilterTypes]):
            The type of filter if this is an atomic node (e.g. `tag`, `attribute`, `text`).
        value (Optional[Union[str, List[str], Dict[str, str]]]):
            The value corresponding to the `filter_type`. Could be a string, a list, 
            or a dictionary, depending on the filter usage.
        operands (Optional[List["Filter"]]):
            Child filters (operands) if this filter is an operator node. For example, 
            an `and` operator might have multiple operands.
    """

    operator: Optional[LogicalOperatorType] = None
    filter_type: Optional[FilterTypes] = None
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    operands: Optional[List["Filter"]] = None

    def __init__(self, operator=None, filter_type=None, value=None, operands=None):
        """
        Initializes a new instance of `Filter`.

        Args:
            operator (LogicalOperatorType, optional):
                Logical operator for this Filter node (e.g. `and`, `or`, `not`). Defaults to None.
            filter_type (FilterTypes, optional):
                Filter type for this Filter node if atomic (e.g. `tag`, `attribute`, `text`). Defaults to None.
            value (Union[str, List[str], Dict[str, str]], optional):
                Corresponding value for the filter type (e.g., the specific tag or attribute). Defaults to None.
            operands (List["Filter"], optional):
                Child Filter nodes if this is a logical operator node. Defaults to None.
        """
        super().__init__(
            action_type=ActionType("filter"),
        )
        self.operator = operator
        self.filter_type = filter_type
        self.value = value
        self.operands = operands

    @classmethod
    def traverse(cls, root: "Filter") -> Iterator["Filter"]:
        """
        Yields all Filter nodes in the tree starting at `root` (including `root`),
        in a pre-order traversal.

        Args:
            root (Filter): The root Filter node to traverse.

        Yields:
            Filter: Each node in the pre-order traversal.
        """
        yield root
        if root.operands:
            for child in root.operands:
                yield from cls.traverse(child)

    @classmethod
    def _classify(cls, raw_content: str) -> bool:
        """
        Determines if the given `raw_content` string represents a Filter.

        Internally, this attempts to parse `raw_content` via `_parse`; 
        if parsing succeeds, it is recognized as a Filter.

        Args:
            raw_content (str):
                The raw DSL statement to classify.

        Returns:
            bool: True if `raw_content` can be parsed as a Filter, False otherwise.
        """
        try:
            cls._parse(raw_content)
            return True
        except Exception as e:
            print(f'Classification Error: {e} (in Filter.py)')
            return False

    @classmethod
    def _parse(cls, raw_content: str):
        """
        Parses the `raw_content` string using `FilterGrammar` to produce a dictionary
        representation of the filter.

        This dictionary is then used by `_build_filter` to create the Filter object.

        Args:
            raw_content (str):
                The DSL statement to be parsed.

        Returns:
            dict: A dictionary representation of the parsed filter structure.

        Raises:
            Exception: If the `FilterGrammar` fails to parse `raw_content`.
        """
        instance: "Filter" = cls()
        instance.assign_metadata(raw_content)
        handler: FilterGrammar = FilterGrammar(instance.metadata["raw_filter"])
        content_as_dict: dict = handler.analyze()
        return content_as_dict

    @classmethod
    def generate(cls, raw_content: str) -> "Filter":
        """
        Constructs a Filter object from a raw DSL statement.

        This method first calls `_parse` to get a dictionary, then 
        `_build_filter` to recursively build a Filter tree.

        Args:
            raw_content (str):
                The raw DSL statement (e.g., "extract from ... where ... -> ...").

        Returns:
            Filter: A fully constructed Filter object.

        Raises:
            ValueError: If the filter structure is unrecognized.
        """
        parsed_data: dict = cls._parse(raw_content)
        filter_obj = cls._build_filter(parsed_data)
        return filter_obj

    @classmethod
    def _build_filter(cls, data: dict) -> "Filter":
        """
        Recursively builds a Filter object from a parsed dictionary.

        The dictionary can represent:
            - A `group` node (enclosed in parentheses),
            - An operator node (`and_operator`, `or_operator`, `not_operator`),
            - An atomic node (`tag`, `attribute`, or `text`).

        Args:
            data (dict):
                Dictionary representing part of the filter tree.

        Returns:
            Filter: The top-level Filter node built from the given data.

        Raises:
            ValueError: If the structure is unrecognized.
        """
        if "group" in data:
            return cls._build_group(data)
        if cls._is_operator_node(data):
            return cls._build_operator(data)
        if cls._is_atomic_node(data):
            return cls._build_atomic(data)
        raise ValueError(f"Unrecognized filter structure: {data}")

    @classmethod
    def _build_group(cls, data: dict) -> "Filter":
        """
        Processes a 'group' node, which corresponds to an expression in parentheses.

        Args:
            data (dict):
                Dictionary with a "group" key whose value should be a single-element list.

        Returns:
            Filter: The Filter node corresponding to what's inside the parentheses.

        Raises:
            ValueError: If the group structure is malformed.
        """
        inner = data["group"]
        if isinstance(inner, list) and len(inner) == 1:
            return cls._build_filter(inner[0])
        else:
            raise ValueError(f"Unexpected structure in group: {data}")

    @classmethod
    def _is_operator_node(cls, data: dict) -> bool:
        """
        Checks if a given dictionary represents a logical operator node (and/or/not).

        Args:
            data (dict):
                The dictionary to check.

        Returns:
            bool: True if the node is an operator node; False otherwise.
        """
        return any(key in ("and_operator", "or_operator", "not_operator") for key in data)

    @classmethod
    def _build_operator(cls, data: dict) -> "Filter":
        """
        Processes an operator node, extracting the operator from the key 
        (e.g., 'and_operator' -> 'and') and building each operand as a child Filter.

        Args:
            data (dict):
                Dictionary containing an operator key and a list of operand dictionaries.

        Returns:
            Filter: A Filter node representing the operator and its operands.

        Raises:
            ValueError: If the operator node key is missing or unrecognized.
        """
        for key, value in data.items():
            if key in ("and_operator", "or_operator", "not_operator"):
                operator = key.split("_")[0]  # e.g., 'and' from 'and_operator'
                operands = [cls._build_filter(child) for child in value]
                return Filter(operator=match_logical_op_type(operator), operands=operands)
        raise ValueError(f"Operator node not found in data: {data}")

    @classmethod
    def _is_atomic_node(cls, data: dict) -> bool:
        """
        Checks if a given dictionary represents an atomic filter node 
        (tag, attribute, or text).

        Args:
            data (dict):
                The dictionary to check.

        Returns:
            bool: True if the node is an atomic filter node; False otherwise.
        """
        return any(key in ("tag", "attribute", "text") for key in data)

    @classmethod
    def _build_atomic(cls, data: dict) -> "Filter":
        """
        Processes an atomic filter node, such as 'tag', 'attribute', or 'text'.
        Determines the filter type and processes the value accordingly.

        Args:
            data (dict):
                Dictionary with a single key of 'tag', 'attribute', or 'text' 
                and a corresponding value.

        Returns:
            Filter: A Filter node for this atomic filter.

        Raises:
            ValueError: If the node structure is unrecognized.
        """
        for key, value in data.items():
            if key in ("tag", "attribute", "text"):
                filter_type_info = {key: value}
                identified_filter_type = match_filter_type(filter_type_info)
                processed_value = cls._process_atomic_value(identified_filter_type, value)
                if identified_filter_type == FilterTypes.UNKNOWN:
                    print(f'Whoops! Unknown filter type: {data}')
                return Filter(filter_type=identified_filter_type, value=processed_value)
        raise ValueError(f"Unrecognized atomic filter structure: {data}")

    @classmethod
    def _process_atomic_value(cls, identified_filter_type, value) -> Union[str, List]:
        """
        Processes the value portion of an atomic filter node.

        - If `value` is a list, each string is unquoted.
        - Dictionaries are examined for "contains" expressions or key-value pairs.
        - If `value` is a string, the quotes are stripped.

        Args:
            identified_filter_type (FilterTypes):
                The determined filter type (e.g. `FilterTypes.TAG`, etc.).
            value (Union[str, list, dict]):
                The raw value from the parse tree.

        Returns:
            Union[str, List]:
                The processed value. Could be a string or a list of strings.

        Raises:
            ValueError: If the structure of the atomic value is unexpected.
        """
        if isinstance(value, list):
            result = []
            for val in value:
                if isinstance(val, str):
                    result.append(val.strip('"'))
                elif isinstance(val, dict):
                    # Check for a "contains" key or a "pair" entry.
                    if identified_filter_type == FilterTypes.ATTRIBUTE_CONTAINS:
                        result.append([v.strip('"') for v in val.get("contains_attr", [])])
                    elif identified_filter_type == FilterTypes.TEXT_CONTAINS:
                        result.append([v.strip('"') for v in val.get("contains_text", [])])
                    else:
                        if "pair" in val:
                            for str_or_pair in val["pair"]:
                                if isinstance(str_or_pair, str):
                                    result.append(str_or_pair.strip('"'))
                                elif isinstance(str_or_pair, dict) and "pair" in str_or_pair:
                                    result.append([v.strip('"') for v in val["pair"]])
                        else:
                            raise ValueError(f"Unrecognized filter structure in atomic value: {val}")
            return result
        elif isinstance(value, str):
            return value.strip('"')
        else:
            return value

    def assign_metadata(self, raw_content: str) -> None:
        """
        Analyzes a DSL statement and extracts three main pieces of metadata:

            1. `from_alias`: The source entity after 'extract from' (optional).
            2. `raw_filter`: The filter portion after 'where' and before '->'.
            3. `assignment`: The alias or target after '->'.

        This method uses two regex patterns:
            - One to match statements of the form: `extract from {alias} where {condition} -> {assignment}`
            - One to match statements of the form: `extract where {condition} -> {assignment}`

        Args:
            raw_content (str):
                The full DSL statement.

        Returns:
            None: Updates the `metadata` dictionary in-place.
        """
        extract_from_where = re.compile(
            r'''^\s*
                extract
                \s+
                from\s+
                (\S+)
                \s+
                where
                \s+(.*?)
                \s*->\s*
                (.+?)
                \s*$''',
            re.VERBOSE | re.DOTALL
        )
        extract_where = re.compile(
            r'''^\s*
                extract
                \s+
                where
                \s+(.*?)
                \s*->\s*
                (.+?)
                \s*$''',
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
        """
        Ensures the consistency of the `Filter` tree:

            - If `operator` is set, there should be at least one operand.
            - If `filter_type` is set, `value` must be present.
            - Recursively validates child operands if present.

        Raises:
            ValueError: If an operator node has no operands, or 
                        if an atomic node has no value.

        Returns:
            bool: True if the filter passes validation.
        """
        if self.operator and not self.operands:
            raise ValueError("Logical operator must have operands")
        if self.filter_type and not self.value:
            raise ValueError("Filter type requires a value")
        if self.operands:
            for operand in self.operands:
                operand.validate()
        return True

    def pretty_print(self, indent=0) -> str:
        """
        Generates a human-readable string representation of the filter tree 
        in a hierarchical format.

        Args:
            indent (int, optional):
                The number of spaces to indent the current node. Defaults to 0.

        Returns:
            str: A formatted multi-line string representing the filter tree.
        """
        indent_str = " " * indent
        lines = [f"{indent_str}Filter({self.operator or ''} {self.filter_type or ''} {self.value or ''})"]
        if self.operands:
            for i, operand in enumerate(self.operands):
                prefix = "└── " if i == len(self.operands) - 1 else "├── "
                lines.append(f"{indent_str}{prefix}{operand.pretty_print(indent + 4)}")
        return "\n".join(lines)

    def __str__(self):
        """
        Returns:
            str: The result of `pretty_print()` for this filter.
        """
        return self.pretty_print()

    def _draw_tree(self, prefix="", is_tail=True):
        """
        Internal helper method to recursively build a list of lines 
        for a tree-like ASCII drawing of the Filter structure.

        Args:
            prefix (str, optional):
                The prefix string used for indentation in the ASCII tree.
            is_tail (bool, optional):
                Whether the current node is the last child of its parent.

        Returns:
            List[str]: A list of string lines representing the tree.
        """
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
        """
        Creates an ASCII-art style representation of the Filter tree structure.

        Returns:
            str: A multi-line string representing the tree.
        """
        return "\n".join(self._draw_tree())
