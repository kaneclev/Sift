from lark import Lark, logger
import logging
logger.setLevel(level=logging.DEBUG)
hl_grammar = """
// Start of the syntax tree (Script (S))
script: target_list (action_list)? 
// Target list definitions (T but RAW)
target_list: _TARGETS~1 TL_REGEX_DEFINITION~1
_TARGETS: /targets\s*=\s*/
TL_REGEX_DEFINITION: /\[([^\]]+)\]/
// Action list (large tree; AL)
action_list: action+
action: target statement_list
target: SOME_TARGET
SOME_TARGET: /[a-zA-Z_^:]+:[\s^\r\n|\r|\n]+/x
// statement list
statement_list: /\{[^\}]*\}/

// Ignoring comments, identified with regex
COMMENTS: /\/\/[^\r\n|\r|\n]+/x

%import common.WS
%ignore WS
%ignore COMMENTS
"""


class HighLevelStructure(Lark):
    def __init__(self, file_contents: str):
        super().__init__(hl_grammar, start='script', parser='lalr')
        self.contents = file_contents
    def parse(self):
        return super().parse(self.contents)
    

