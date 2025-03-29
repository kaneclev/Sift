from dataclasses import dataclass
from typing import Dict, List, Union

from language.parsing.ast.enums import HTMLPropertyType


@dataclass
class HTMLProperty:
    htype: HTMLPropertyType
    detail: Union[str, List, Dict]
    def __str__(self):
        return f'{self.htype.value} {self.detail}'

