import os

from api.parsing_api.ipc_management.ipc_manager import (
    IPC,
    Formats,
    IPCOptions,
    Recipients,
)
from file_operations.script_representations import ScriptObject
from language.IR.ir_base import IntermediateRepresentation
from language.IR.read_tree import TreeReader
from language.parsing.ast.script_tree import ScriptTree
from language.parsing.parser import Parser

DEBUG_LOG_DIR = os.environ["DEBUG_LOGS"]

################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, script: ScriptObject):
        # TODO: This class might need to be the one to handle error propogation.
        """ API For parsing and generating IR for a sift script.

        Args:
            script (ScriptObject): The script object to process (must inherit from ScriptObject)
        """
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
        if not self.script.is_verified:
            print("\nCannot begin to parse script.")
            self.script.issues.describe()
            return []
        ast = Parser(self.script.get_content()).parse_content_to_tree()
        ir = TreeReader.to_ir(ast, identifier=self.script.get_id())
        return [ast, ir]
