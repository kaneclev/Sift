from dataclasses import dataclass, field
from typing import Dict

from language.parsing.exceptions.internal_exception import NoStartRuleError


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
        used = {}
        start_production = None
        start_prod_name = self.start
        start_production = self.production_map.get(start_prod_name, None)
        if start_production is None:
            raise NoStartRuleError("to_string", self.start)
        else:
            grammar_list.append(": ".join([self.start, start_production]))
            used[self.start] = True
        for rule_name, production_definition in self.production_map.items():
            if used.get(rule_name, None) is None:
                grammar_list.append(": ".join([rule_name, production_definition]))
                used[rule_name] = True
        grammar_list.append(self._comment_identifier)
        for imp in self._imports:
            grammar_list.append(imp)
        # Finally, join them separated by newlines.
        return "\n".join(grammar_list)
