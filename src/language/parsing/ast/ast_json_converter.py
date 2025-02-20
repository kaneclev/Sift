
from dataclasses import asdict

import orjson

from language.parsing.ast.script_tree import ScriptTree


class SiftASTConverter:
    """ Utility class for converting a ScriptTree object into different forms. """

    def __init__(self, ast: ScriptTree, filename: str):
        """ Constructor.
        Takes a ScriptTree object (ast) and the *base name* of the file used to generate the ScriptTree.
        From there, callers can morph the ScriptTree into different forms provided by the SiftASTConverter

        Keyword arguments:
        ast: (ScriptTree) The tree we will perform conversions with.
        filename: (str) The base name of the file used to generate the ScriptTree, used for storing converted representations of the ScriptTree (like JSON).
        """
        self.tree = ast
        filename = filename.split('.')[0] + ".json"
        self.json_path = f"../json_conversions/{filename}"
        pass

    def to_json(self, should_store: bool) -> dict:
        """ Converts the ScriptTree dataclass into a JSON string representation.
        If 'store_repr_as_file' was true on object creation, the JSON representation of the ScriptTree
        is stored under Sift/json_conversions/ using the filename that was provided on creation.

        Keyword arguments:
        bool: should_store, a boolean deciding if we store the json as a file or not.
        Return: (str) The JSON representation of the ScriptTree dataclass.
        """

        json_bytes = orjson.dumps(asdict(self.tree), option=orjson.OPT_INDENT_2)
        if should_store:
            with open(self.json_path, "wb") as f:
                f.write(json_bytes)
        return orjson.loads(json_bytes)

