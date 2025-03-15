import os

from typing import Dict

from api.ipc_management.ipc_manager import IPC
from api.ipc_management.ipc_options import ComTypes, IPCOptions, MsgType, Recievers
from file_operations.sift_file import ScriptTree, SiftFile
from IR.ir_base import IntermediateRepresentation
from IR.ir_format_conversion import IRConverter
from IR.read_tree import TreeReader
from language.parsing.ast.ast_json_converter import SiftASTConverter


################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, sift_file: str, **options):
        """ API For parsing and generating IR for a sift script.

        Args:
            sift_file (str): The file to process.
            pickle: Default True. Pickles the IR and sends it to Sift/IRConversions under the sift file filename.
            show_ast: Default False. Shows the generated AST after parsing.
            show_pkl: Default False. Unpickles the IR, shows the pickle-loaded object.
            show_json_ast: Default False. Shows the JSON representation of the AST object.
            save_json_ast: Default False. Saves the JSON conversion of the AST to the IRConversions folder under the sift file filename.
            send (list[IPCOptions]): Defaults to [ IPCOptions(com_type=ComTypes.FILESYS, msg_type=MsgType.JSON, recipient=Recievers.REQUEST_MANAGER) ]
        """
        # To allow for value-checking without 'no variable exists' issues.
        self.sift_file_path: str = None
        self.sift_file_basename: str = None
        self.sift_file_instance: SiftFile = None
        self.options: Dict[str, bool] = None
        self.ast: ScriptTree = None


        self.sift_file_path = sift_file
        self.sift_file_basename = os.path.basename(sift_file)
        self.options = {
            "pickle": True,
            "send": [
                IPCOptions(com_type=ComTypes.FILESYS, msg_type=MsgType.JSON, recipient=Recievers.REQUEST_MANAGER)
            ],
            "show_ast": False,
            "show_pkl": False,
            "show_json_ast": False,
            "save_json_ast": False,
        }
        self.options.update(options)
        self.sift_file_instance = self._generate_siftfile()
        self.ast = self._generate_ast()
        self.ir_obj = self.to_ir()
        self._option_handler()
        pass

    def _option_handler(self):
        json_ast = None
        make_json_ast = self.options.get('show_json_ast') or self.options.get('save_json_ast')
        pkl_obj = None
        make_pkl = self.options.get('pickle') or self.options.get('show_pickle')
        if make_pkl:
            pkl_obj = IRConverter.to_pickle(ir_obj=self.ir_obj)
        if make_json_ast:
            json_conversion_options = {}
            if self.options.get('save_json_ast', None) is not None:
                json_conversion_options[SiftASTConverter.ConversionOptions.SAVE_FILE] = True
            json_ast = SiftASTConverter.to_json(ast=self.ast, file_name=self.sift_file_basename, options=json_conversion_options)

        for opt, val in self.options.items():
            if val:
                match opt:
                    case 'show_ast':
                        self.sift_file_instance.show_tree()
                        pass
                    case 'show_json_ast':
                        print(json_ast)
                        pass
                    case 'save_json_ast':
                        pass
                    case 'show_pickle':
                        print(pkl_obj)
                        pass
                    case 'pickle':
                        pass
                    case 'send':
                        IPC.send(ir_obj=self.ir_obj, options=val)
                    case _:
                        raise ValueError(f"Unknown option: {opt}")

    def _generate_siftfile(self) -> SiftFile:
        """ Private method for generating a SiftFile instance.
        self.sift_file is the file path to the file we will be parsing.
        The SiftFile class will immediately validate the SiftFile, so that we know its good to parse.'
        Args
        ----
            None.
        Returns
        -------
            SiftFile -- A new SiftFile instance.
        """
        return SiftFile(self.sift_file_path)

    def _generate_ast(self) -> ScriptTree:
        if not self.sift_file_instance:
            raise ValueError(f'Expected a valid SiftFile instance to create the ScriptTree with. \
                             Instead, it was {self.sift_file_instance}')
        return self.sift_file_instance.parse_file()



    def to_ir(self) -> IntermediateRepresentation:
        ir_tree = TreeReader.to_ir(self.ast, self.sift_file_basename)
        return ir_tree

