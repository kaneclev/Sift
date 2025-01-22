from dataclasses import dataclass
from Language.Structs.ActionTypes import ActionType
from Language.Structs.Filter import Filter
from Language.Structs.PreciseGrammars.ActionGrammar import analyze
@dataclass
class Action:
    action_type: ActionType
    filter_: Filter
    @classmethod
    def generate_action(cls, action_string: str):
        # Use the ActionGrammar class's analyze method to get a dict representation of the language
        analyzed = analyze(string_content_to_analyze=action_string)
        # Grab elements relevant to my class, pass elements relevant to the Filter class to the proper filter constructor
        generated_action_type = ActionType.define_action_type(analyzed)
        filt = Filter.generate_filter(analyzed["filter_statement"])
        return cls(action_type=generated_action_type, filter_=filt)
    
    def pretty_print(self, indent=0) -> str:
        indent_str = " " * indent
        lines = []
        lines.append(f"{indent_str}Action:")
        lines.append(f"{indent_str}  action_type: {self.action_type}")
        lines.append(f"{indent_str}  filter: {self.filter_.pretty_print(indent=indent + 2)}")
        return "\n".join(lines)
    
    def __str__(self):
        # If you want to override __str__ in the same style
        return self.pretty_print(indent=0)