import os

from typing import Dict, List

from api.ipc_management.ipc_manager import IPC
from api.ipc_management.ipc_options import ComTypes, IPCOptions, MsgType, Recievers
from file_operations.sift_file import ScriptTree, SiftFile
from IR.ir_base import IntermediateRepresentation
from IR.ir_format_conversion import IRConverter
from IR.read_tree import TreeReader
from language.parsing.ast.ast_json_converter import SiftASTConverter
from shared.utils.file_conversions import FileConverter, FileOpts

DEBUG_LOG_DIR = os.environ["DEBUG_LOGS"]

################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, sift_file: str, ast: Dict = None,
                 json: Dict = None, pickle: Dict = None,
                 send: List[IPCOptions] = None):
        """ API For parsing and generating IR for a sift script.

        Args:
            sift_file (str): The file to process.
            ast (dict): Default {"save": False, "show": False}. Saves to debug_logs, prints to stdout. (The string representation of the AST object)
            json (dict): Default {"save": False, "show": False}. JSON-oriented AST options. Saves to json_conversions by default. Prints to stdout.
            pickle (dict): Default {"show": False, "save": False}. Pickles the IR and sends it to Sift/IRConversions under the sift file filename. Optionally prints to stdout.
            send (list[IPCOptions]): Defaults to [ IPCOptions(com_type=ComTypes.FILESYS, msg_type=MsgType.JSON, recipient=Recievers.REQUEST_MANAGER) ]
                Given a list of IPC (Inter-Process Communication) options, sends the IR data as specified.
        """
        # To allow for value-checking without 'no variable exists' issues.
        self.sift_file_path: str = None
        self.sift_file_basename: str = None
        self.sift_file_instance: SiftFile = None
        self.options: Dict[str, bool] = None
        self.ast: ScriptTree = None


        self.sift_file_path = sift_file
        self.sift_file_basename = os.path.basename(sift_file)
        default_options = {
            "pickle": {"save": False, "show": False},
            "json": {"save": False, "show": False},
            "ast": {"save": False, "show": False},
            "send": [IPCOptions(com_type=ComTypes.FILESYS, msg_type=MsgType.JSON, recipient=Recievers.REQUEST_MANAGER)]
        }

        self.options = {
            "pickle": {**default_options["pickle"], **(pickle or {})},
            "json": {**default_options["json"], **(json or {})},
            "ast": {**default_options["ast"], **(ast or {})},
            "send": send if send is not None else default_options["send"]
        }

        self.script = self._generate_siftfile()
        self.ast = self._generate_ast()
        self.ir_obj = self.to_ir()
        self._option_handler()
        pass
    def _handle_ast_options(self, options: Dict):
        txt_ast = None
        save = options.get('save', False)
        show = options.get('show', False)
        if save or show:
            txt_ast = str(self.script.get_tree_obj())
        if save:
            # We write to debug_logs by default.
            FileConverter.save_as(save_to_dir=DEBUG_LOG_DIR,
                                    raw_basename=os.path.basename(self.script.file_path),
                                    ftype=FileOpts.TXT, object_to_save=txt_ast)
        if show:
            print(txt_ast)

    def _handle_json_options(self, options: Dict):
        json_ast = None
        save = options.get('save', False)
        show = options.get('show', False)
        if save or show:
            opts = {
                SiftASTConverter.ConversionOptions.SAVE_FILE: save,
                SiftASTConverter.ConversionOptions.FILE_NAME: os.path.basename(self.script.file_path)
                }
            json_ast = SiftASTConverter().to_json(ast=self.ast, options=opts)
            if show:
                print(json_ast)

    def _handle_pickle_options(self, options: Dict):
        pkl_obj = None
        save = options.get('save', False)
        show = options.get('show', False)
        if save or show:
            opts = {
                IRConverter.ConversionOptions.SAVE_FILE: save,
            }
            pkl_obj = IRConverter.to_pickle(ir_obj=self.ir_obj, options=opts)
            if show:
                print(pkl_obj)

    def _option_handler(self):
        for opt, val in self.options.items():
            if val:
                match opt:
                    case 'ast':
                        self._handle_ast_options(options=val)
                        pass
                    case 'json':
                        self._handle_json_options(options=val)
                        pass
                    case 'pickle':
                        self._handle_pickle_options(options=val)
                        pass
                    case 'send':
                        IPC.send(ir_obj=self.ir_obj, options=val)
                    case _:
                        if self.options.get(opt, None) is None:
                            raise ValueError(f"Unknown option: {opt}")
                        else:
                            ...

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
        if not self.script:
            raise ValueError(f'Expected a valid SiftFile instance to create the ScriptTree with. \
                             Instead, it was {self.script}')
        return self.script.parse_file()

    def to_ir(self) -> IntermediateRepresentation:
        ir_tree = TreeReader.to_ir(self.ast, os.path.basename(self.script.file_path))
        return ir_tree

