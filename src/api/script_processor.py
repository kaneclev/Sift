import os

from typing import Dict, List

from file_operations.sift_file import ScriptTree, SiftFile
from language.parsing.ast.ast_json_converter import SiftASTConverter


################################################
# #! Main API For Parsing SiftScripts
################################################
class ScriptProcessor:
    def __init__(self, sift_file: str, **options):
        self.sift_file = sift_file
        self.sift_file_basename = os.path.basename(sift_file)
        self.options = {
            "show_ast": False,
            "show_json": False,
            "save_json": False,
        }
        self.options.update(options)

        self.sift_file_instance = self._generate_siftfile()
        self.ast = self._generate_ast(self.sift_file_instance)
        self.json = None
        self._option_handler()
        pass

    def _option_handler(self):
        save_json = self.options.get('save_json')
        converter = SiftASTConverter(self.ast, self.sift_file_basename)
        # NOTE: We always convert to json for queue reasons regardless of if the options suggest we save, show or not.
        self.json = converter.to_json(should_store=save_json)

        if self.options.get('show_ast'):
            self.sift_file_instance.show_tree()
        if self.options.get('show_json'):
            print(f'JSON representation: \n {self.json}')

    def to_queue(self):
        ...


    def _generate_siftfile(self) -> SiftFile:
        return SiftFile(self.sift_file)

    def _generate_ast(self, siftfile_instance: SiftFile) -> ScriptTree:
        return siftfile_instance.parse_file()
