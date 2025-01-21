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
    def generate_filter(cls, filter_string: str):
        # TODO: Fix this method. Filter ought to be a tree-like structure.
        """
        Generates a Filter tree from a filter string.

        Args:
            filter_string (str): The filter string to parse.

        Returns:
            Filter: The constructed Filter tree.

        Raises:
            ValueError: If the input data is invalid or cannot be parsed.
        """
        try:
            # Parse the string into intermediate data
            data = analyze(filter_string=filter_string)
            print(f"Parsed Data: {data}")

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

        except Exception as e:
            raise ValueError(f"Error generating filter from string: {filter_string}. Details: {str(e)}")
