from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GrammarContainer:
    start: str = None
    production_map: Dict[str, str] = field(default_factory=dict)
    parser: str = field(default="lalr")

    _comment_identifier = "COMMENTS: /\\/\\/[^\r\n|\r|\n]+/x"
    _imports = [
        r"%import common.WS",
        r"%ignore WS",
        r"%ignore COMMENTS",
        r"%import common.ESCAPED_STRING"
    ]

    def to_string(self):
        grammar_list = []
        for rule_name, production_definition in self.production_map.items():
            grammar_list.append(": ".join([rule_name, production_definition]))
        grammar_list.append(self._comment_identifier)
        for imp in self._imports:
            grammar_list.append(imp)
        # Finally, join them separated by newlines.
        return "\n".join(grammar_list)
