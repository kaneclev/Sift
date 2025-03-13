from dataclasses import dataclass


@dataclass
class ActionType:
    plugin_name: str
    def __init__(self, name: str):
        self.plugin_name = name
    def __hash__(self):
        return hash(self.plugin_name)
    def __repr__(self):
        return self.plugin_name
    def __str__(self):
        return self.plugin_name

