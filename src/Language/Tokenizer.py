import os
import re
from enum import Enum
""" TOKENIZER DEFINITIONS
Here's an outline of the grammar of a SiftFile. 
Right now a siftfile will start with:


"""

class Tokens:
    class Statements(Enum):
        EXTRACT = re.compile(r'\s*extract\s+where([*^;]+);')
        TARGET_DEFINITIONS = "targets"

    class Operator(Enum):
        COMMA = ","
        COLON = ":"
        AND = "and"
        OR = "or"
        NOT = "not"
        VARIABLE_ASSIGNMENT = re.compile(r'->\s*([a-zA-Z_]+)\s*;')

    class Groupings(Enum):
        ACTION_BLOCK = re.compile(rf'')
        GROUPING = re.compile(rf'(\(.*?\))')
        LIST = "["
        # Groupings are defined within **Statements** but a grouping alone is not a statement
        # A statement may contain any number of groupings
        # A grouping may contain a list, and a list may contain a grouping.




    STRING = '"'


class Tokenizer:
    def __init__(self, file_as_string: str):
        """ Constructor for Tokenizer
        
        Keyword arguments:
        file_as_string: str -> The pre-validated, confirmed-to-exist valid sift file. 
        Return: Instance of the Tokenizer class.
        """
        self.file_contents = ""
        with open(file_as_string, 'r') as siftfile:
            self.file_contents = siftfile.read()
        pass
    def show_contents(self):
        print(repr(self.file_contents))

    def get_tokens(self) -> list:
        pass


a = Tokenizer(r"C:\Users\Kane\projects\Sift\siftscripts\example.sift")
a.get_tokens()