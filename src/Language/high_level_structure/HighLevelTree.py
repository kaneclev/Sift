from lark import Transformer
from copy import deepcopy
import json

from Language.high_level_structure.HighLevelGrammar import HighLevelStructure

class HighLevelTree:
    def __init__(self, file_contents: str):
        self.parse_tree = HighLevelStructure(file_contents=file_contents).parse()
        self.tree = HLTransformer().transform(self.parse_tree)
        pass
    def print_tree(self):
        print(json.dumps(self.tree, indent=4))
        return json.dumps(self.tree, indent=4)
    def get_tree(self):
        return deepcopy(self.tree)
class HLTransformer(Transformer):
    def script(self, tree):
        target_list = tree[0]
        if len(tree) > 1:
            action_list = tree[1]
        else:
            action_list = []
        return {"target_list": target_list, "action_list": action_list}
    def target_list(self, tree):
        token = tree[0]
        return token.value
    def action_list(self, tree):
        return tree
    def action(self, tree):
        target_tree, statement_list = tree
        target = target_tree.children[0].value
        return {"target": target, "statement_list": statement_list}
    def statement_list(self, tree):
        token = tree[0]
        statement_list_content = token.value
        return statement_list_content


