from dataclasses import asdict

import orjson

from language.parsing.ast.script_tree import ScriptTree


class SiftASTConverter:
    def __init__(self, ast: ScriptTree):
        self.tree = ast
        pass
    def to_json(self):
        json_bytes = orjson.dumps(asdict(self.tree), option=orjson.OPT_INDENT_2)

        json_str = json_bytes.decode("utf-8")
        print(json_str)