import re

from dataclasses import dataclass  # noqa: N999
from typing import Dict, List, Optional, Union

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
        #! Interface Implementation from ParsedNode
        """ Determines if the raw_content string is a Filter or not. """
        try:
            cls._parse(raw_content)
            return True
        except Exception as e:
            print(f'Classification Error: {e} (in Filter.py)')
            return False

    @classmethod
    def _parse(cls, raw_content: str):
        #! Interface Implementation from ParsedNode
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
        parsed_data: dict = cls._parse(raw_content)
        return cls._build_filter(parsed_data)


    @classmethod
    def _build_filter(cls, data: dict) -> "Filter":
        """
        Recursively builds a Filter instance from a parsed dictionary.
        This method expects the dictionary to have one key at the top level.
        That key is either an operator (e.g. 'and_operator', 'or_operator', 'not_operator')
        or an atomic filter type ('tag', 'attribute', or 'text').
        """
        # Handle operator nodes first.
        print(f'here i am in buold filter {data}')
        for key, value in data.items():
            if key in ("and_operator", "or_operator", "not_operator"):
                # Extract the operator string (e.g. 'and', 'or', 'not')
                operator = key.split("_")[0]
                # 'value' here should be a list of dictionaries representing the operands.
                operands = [cls._build_filter(child) for child in value]
                return Filter(operator=match_logical_op_type(operator), operands=operands)

        # Otherwise, assume it's an atomic filter node.
        # The key here should be one of: 'tag', 'attribute', or 'text'
        # (if your grammar ever produces additional keys, add them here)
        for key, value in data.items():
            if key in ("tag", "attribute", "text"):
                filter_type = {key: value}  # You might want to map this to your FilterTypes enum.
                # If 'value' is a list of tokens (as strings with quotes), remove the quotes.
                if isinstance(value, list):
                    print(f'Value: {value}')
                    # Remove leading and trailing quotes from each string.
                    for val in value: # then its of the type: ['class', 'some_name'] OR ['class', {'contains': 'some_name'}]
                        if isinstance(val, str):
                            processed_value = val.strip('"')
                        elif isinstance(val, dict):
                            if val.get("contains", None):
                                processed_value = [v.strip() for v in val["contains"]]
                            else: # Then it is a LIST of Pairs; like:  [{'pair': ['"class"', '"price"']}, {'pair': ['"class"', '"discount"']}]
                                # need to iterate over the list and extract the pairs
                                if val.get("pair", None):
                                    processed_value = [v.strip() for v in val["pair"]]
                                else:
                                    raise ValueError(f"Unrecognized filter structure: {data}")
                elif isinstance(value, str):
                    processed_value = value.strip('"')
                else:
                    processed_value = value
                identified_filter_type = match_filter_type(filter_type)
                if identified_filter_type == FilterTypes.UNKNOWN:
                    print(f'Whoops! Unknown filter type: {data}')
                # For an atomic filter, there are no operands.
                return Filter(filter_type=identified_filter_type, value=processed_value)

        raise ValueError(f"Unrecognized filter structure: {data}")


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
        # ! Interface Implementation from ParsedNode
        # TODO maybe make more robust
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
