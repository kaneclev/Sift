from dataclasses import dataclass
from typing import Union, List, Dict
from Language.Structs.FilterTypes import FilterType
from Language.Structs.Condition import Condition
@dataclass
class Filter:
    filter_type: FilterType  # Filter type: "tag", "attribute", "text"
    conditions: List[Condition]
    values: Union[List[str], Dict[str, str]]  # Values for filtering (e.g., tags, attributes, etc.)
