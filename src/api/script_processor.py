import os

from typing import Dict

from file_operations.sift_file import ScriptTree, SiftFile
from IR.ir_base import IntermediateRepresentation
from IR.read_tree import TreeReader
from language.parsing.ast.ast_json_converter import SiftASTConverter


################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, sift_file: str, **options):
        # To allow for value-checking without 'no variable exists' issues.
        self.sift_file_path: str = None
        self.sift_file_basename: str = None
        self.sift_file_instance: SiftFile = None
        self.options: Dict[str, bool] = None
        self.ast: ScriptTree = None
        self.json = None


        self.sift_file_path = sift_file
        self.sift_file_basename = os.path.basename(sift_file)
        self.options = {
            "show_ast": False,
            "show_json": False,
            "save_json": False,
        }
        self.options.update(options)
        self.sift_file_instance = self._generate_siftfile()
        self.ast = self._generate_ast()
        self._option_handler()
        pass


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

    def _option_handler(self):
        save_json = self.options.get('save_json')
        converter = SiftASTConverter(self.ast, self.sift_file_basename)
        # NOTE: We always convert to json for queue reasons regardless of if the options suggest we save, show or not.
        self.json = converter.to_json(should_store=save_json)
        if not self.json:
            raise ValueError(f'There was an issue converting the AST to JSON representation: (self.json = {self.json})')
        if self.options.get('show_ast'):
            self.sift_file_instance.show_tree()
        if self.options.get('show_json'):
            print(f'JSON representation: \n {self.json}')

    def to_ir(self) -> IntermediateRepresentation:
        return TreeReader.to_ir(self.ast)

