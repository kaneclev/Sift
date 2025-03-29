import os

from api.language_api.ipc_management.ipc_manager import (
    IPC,
    Formats,
    IPCOptions,
    Recipients,
)
from api.language_api.script_representations import (
    RepresentationType,
    ScriptObject,
    get_script_object,
)
from language.compiler.compiler import Compiler
from language.compiler.ir_base import IntermediateRepresentation
from language.compiler.ir_format_conversion import IRConverter
from language.parsing.ast.script_tree import ScriptTree
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
        self.script: ScriptObject = script
        pass

    def make_message(self, ir: IntermediateRepresentation, recipient: Recipients, correlation_id: str):
        options = IPCOptions(recipient=recipient, format_=Formats.AMPQ, correlation_id=correlation_id)
        if not ir:
            ir = self.to_ir()
        if not isinstance(options, list):
            options = [options]
        confirmations = IPC.create(ir_obj=ir, translations=options)
        return confirmations

    def parse(self) -> list[ScriptTree, IntermediateRepresentation]:
        is_debug = False
        if not self.script.is_verified:
            print("\nCannot begin to parse script.")
            self.script.issues.describe()
            return []
        ast = Parser(self.script.get_content()).parse_content_to_tree()
        ir = Compiler.to_ir(ast, identifier=self.script.get_id())
        if (flag := os.environ.get('PARSER_DEBUG', None)) is not None:
            if flag == "1":
                is_debug = True
        if is_debug:
            IRConverter.to_json(ir_obj=ir)
        return [ast, ir]
