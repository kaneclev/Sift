import os

from typing import List, Union

from api.ipc_management.ipc_manager import IPC
from api.ipc_management.ipc_options import ComTypes, IPCOptions, MsgType, Recievers
from file_operations.script_representations import ScriptObject
from IR.ir_base import IntermediateRepresentation
from IR.read_tree import TreeReader
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

    def send_ir(self, ir: IntermediateRepresentation, options: Union[IPCOptions, List[IPCOptions]] = None):
        if not options:
            options = IPCOptions(com_type=ComTypes.FILESYS, msg_type=MsgType.JSON, recipient=Recievers.REQUEST_MANAGER)
        if not ir:
            ir = self.to_ir()
        if not isinstance(options, list):
            options = [options]
        confirmations = IPC.send(ir_obj=ir, options=options)
        return confirmations

    def parse(self) -> list[ScriptTree, IntermediateRepresentation]:
        if not self.script.is_verified:
            print("\nCannot begin to parse script.")
            self.script.issues.describe()
            return []
        ast = Parser(self.script.get_content()).parse_content_to_tree()
        ir = TreeReader.to_ir(ast, identifier=self.script.get_id())
        return [ast, ir]
