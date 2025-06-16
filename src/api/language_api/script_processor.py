import os

from typing import List, Union

from api.language_api.script_representations import (
    RepresentationType,
    ScriptObject,
    ScriptObjectIssues,
    get_script_object,
)
from language.parsing.ast.trees import ScriptTree
from language.parsing.parser import Parser
from logging import Logger

DEBUG_LOG_DIR = os.environ["DEBUG_LOGS"]
processor_logger: Logger = Logger("ScriptProcessor")
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
        self.is_valid_script = False
        if not isinstance(script, ScriptObject):
            # Then we are being fed a file manually thru cmd args.
            script = get_script_object(raw=script, rtype=RepresentationType.FILE)
        self.script: Union[ScriptObject, ScriptObjectIssues] = script
        self.is_valid_script = self._verify_representation()
        if self.is_valid_script:
            self.id = self.script.get_id()
        pass

    def _verify_representation(self) -> bool:
        if isinstance(self.script, ScriptObjectIssues):
            return False
        return True

    def parse(self) -> ScriptTree:
        if not self.is_valid_script:
            # Then we can safely assume that the Script object is actually of type ScriptObjectIssue, which has a describe method
            assert(isinstance(self.script, ScriptObjectIssues), "If self.is_valid_script is False, it must be true that self.script is a ScriptObjectIssues object.")
            return self.script.get_issues()
        ast = Parser(self.script.get_content()).parse_content_to_tree()

        return ast
