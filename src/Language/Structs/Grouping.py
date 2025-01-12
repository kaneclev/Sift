from dataclasses import dataclass
from typing import List
from Language.Structs.Condition import Condition

@dataclass
class Grouping: # for groups of filters/conditions
    conditions: List[Condition] 
