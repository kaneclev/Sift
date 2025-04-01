import os

from typing import List, Union

from api.language_api.script_representations import (
    RepresentationType,
    ScriptObject,
    ScriptObjectIssues,
    get_script_object,
)
from language.compiler.compiler import CompiledScript, Compiler
from language.compiler.intermediate_representation import IntermediateRepresentation
from language.parsing.ast.trees import ScriptTree
from language.parsing.parser import Parser

DEBUG_LOG_DIR = os.environ["DEBUG_LOGS"]

################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, script):
        # TODO: This class might need to be the one to handle error propogation.
        """ API For parsing and generating IR for a sift script.

        Args:
            script (ScriptObject): The script object to process (must inherit from ScriptObject)
        """
        if not isinstance(script, ScriptObject):
            # Then we are being fed a file manually thru cmd args.
            script = get_script_object(raw=script, rtype=RepresentationType.FILE)
        self.script: Union[ScriptObject, ScriptObjectIssues] = script
        pass

    def _verify_representation(self) -> bool:
        if isinstance(self.script, ScriptObjectIssues):
            print(self.script.describe())
            return False
        return True

    def parse(self) -> List[Union[ScriptTree, IntermediateRepresentation]]:
        is_valid_script = self._verify_representation()
        if not is_valid_script:
            return []
        ast = Parser(self.script.get_content()).parse_content_to_tree()

        compiler = Compiler(AST=ast, script_id=self.script.get_id())

        compiled_object: CompiledScript = compiler.compile()
        ir, bytecode = compiled_object.IR, compiled_object.BYTECODE  # noqa: F841

        if (flag := os.environ.get('PARSER_DEBUG', None)) is not None:
            if flag == "1":
                is_debug = True  # noqa: F841
                # TODO: Now what?

        return [ast, ir]
