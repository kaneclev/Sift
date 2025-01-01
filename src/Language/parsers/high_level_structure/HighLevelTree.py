from parsers.high_level_structure.HighLevelGrammar import LangStructure
from lark import Transformer
import json
class HighLevelTree:
    def __init__(self, file_contents: str):
        self.parse_tree = LangStructure(file_contents=file_contents).parse()
        self.tree = HLTransformer().transform(self.parse_tree)
        pass
    def print_tree(self):
        print(json.dumps(self.tree, indent=4))
class HLTransformer(Transformer):
    def script(self, tree):
        target_list, action_list = tree
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


