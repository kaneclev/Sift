from language.parsing.high_level_structure.high_level_tree import HighLevelTree
from language.parsing.structs.script_tree import ScriptTree


class Parser:
    def __init__(self, script_content: str):
        self.raw_content = script_content
        self.high_level_tree = HighLevelTree(self.raw_content)
        pass

    def parse_content_to_tree(self):
        return ScriptTree.generate(self.high_level_tree)
