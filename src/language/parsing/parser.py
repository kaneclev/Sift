from language.parsing.ast.high_level_structure.high_level_tree import HighLevelTree
from language.parsing.ast.script_tree import ScriptTree


class Parser:
    """
    The Parser class is used as an interface between the SiftFile class
    and the parsing and transformation logic for generating the script AST.
    """
    def __init__(self, script_content: str):
        """ Creates a Parser instance given the entire content of the Sift script.

        Given the script content, we use the HighLevelTree class to create an intermediate
        representation of the Script content.

        Args:
            script_content (str): The content of the Sift file to be parsed.
        """
        self.raw_content = script_content
        self.high_level_tree = HighLevelTree.generate(script_content)
        pass

    def parse_content_to_tree(self) -> ScriptTree:
        """ Uses ScriptTree to generate the AST.

        Using the intermediate representation Parser generated on construction,
        parse_content_to_tree() provides that representation to ScriptTree's factory method,
        who then uses that structure to define the AST.

        Returns:
            ScriptTree: The AST representation of the Sift script.
        """
        return ScriptTree.generate(self.high_level_tree)
