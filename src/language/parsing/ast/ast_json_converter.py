
from dataclasses import asdict

import orjson

from language.parsing.ast.script_tree import ScriptTree


class SiftASTConverter:
    """ Utility class for converting a ScriptTree object into different forms. """

    def __init__(self, ast: ScriptTree, filename: str, store_repr_as_file: bool = False):
        """ Constructor.
        Takes a ScriptTree object (ast) and the *base name* of the file used to generate the ScriptTree.
        From there, callers can morph the ScriptTree into different forms provided by the SiftASTConverter
        
        Keyword arguments:
        ast: (ScriptTree) The tree we will perform conversions with.
        filename: (str) The base name of the file used to generate the ScriptTree, used for storing converted representations of the ScriptTree (like JSON).
        store_repr_as_file: (bool) 
            If true, conversions like to_json will be stored in a dedicated folder using the 'filename' parameter passed to the constructor.
            Defaults to false.
        """
        self.should_store = store_repr_as_file
        self.tree = ast
        filename = filename.split('.')[0] + ".json"
        self.json_path = f"../json_conversions/{filename}"
        pass

    def to_json(self) -> str:
        """ Converts the ScriptTree dataclass into a JSON string representation.
        If 'store_repr_as_file' was true on object creation, the JSON representation of the ScriptTree
        is stored under Sift/json_conversions/ using the filename that was provided on creation.
        
        Keyword arguments:
        None.
        Return: (str) The JSON representation of the ScriptTree dataclass.
        """

        json_bytes = orjson.dumps(asdict(self.tree), option=orjson.OPT_INDENT_2)
        if self.should_store:
            with open(self.json_path, "wb") as f:
                f.write(json_bytes)
        return orjson.loads(json_bytes)

