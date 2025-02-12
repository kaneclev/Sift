import os

from dataclasses import asdict

import orjson

from language.parsing.ast.script_tree import ScriptTree


class SiftASTConverter:
    def __init__(self, ast: ScriptTree, filename: str):
        self.tree = ast
        filename = filename.split('.')[0] + ".json"
        self.json_path = f"../json_conversions/{filename}"
        pass
    def to_json(self):
        json_bytes = orjson.dumps(asdict(self.tree), option=orjson.OPT_INDENT_2)
        with open(self.json_path, "wb") as f:
            f.write(json_bytes)
        return orjson.loads(json_bytes)

