from dataclasses import dataclass
from typing import List

@dataclass
class Condition:
    operator: str # like and or not
    contains: bool
    