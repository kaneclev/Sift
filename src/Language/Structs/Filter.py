from dataclasses import dataclass
from typing import Dict, Optional, List, Union
from Language.Structs.PreciseGrammars.FilterTypes import FilterTypes

from Language.Structs.PreciseGrammars.FilterGrammar import analyze
from Language.Structs.PreciseGrammars.ExpressionTypes import LogicalOperatorType
@dataclass
class Filter:
    operator: Optional[LogicalOperatorType] = None
    filter_type: Optional[FilterTypes] = None
    value: Optional[Union[str, List[str], Dict[str, str]]] = None
    operands: Optional[List["Filter"]] = None

    @classmethod
    def generate_filter(cls, filter_content: str):
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
