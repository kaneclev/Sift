from dataclasses import dataclass
from typing import List
from Language.Structs.Filter import Filter

@dataclass
class Condition:
    operator: str # like and or not
    contains: bool
    