import logging

from lark import Lark, Transformer, logger

logger.setLevel(level=logging.DEBUG)
hl_grammar = """
// Start of the syntax tree (Script (S))
script: target_list (action_list)?
// Target list definitions (T but RAW)
target_list: _TARGETS~1 TL_REGEX_DEFINITION~1
_TARGETS: /targets\\s*=\\s*/
TL_REGEX_DEFINITION: /\\[([^\\]]+)\\]/
// Action list (large tree; AL)
action_list: action+
action: target statement_list
target: SOME_TARGET
SOME_TARGET: /[a-zA-Z_^:]+:[\\s^\r\n|\r|\n]+/x
// statement list
statement_list: /\\{[^\\}]*\\}/

// Ignoring comments, identified with regex
COMMENTS: /\\/\\/[^\r\n|\r|\n]+/x

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

class HLTransformer(Transformer):
    def script(self, tree):
        target_list = tree[0]
        if len(tree) > 1:
            action_list = tree[1]
        else:
            action_list = []
        return {"target_list": target_list, "action_list": action_list}
    def target_list(self, tree):
        token = tree[0]
        return token.value
    def action_list(self, tree):
        return tree
    def action(self, tree):
        target_tree, statement_list = tree
        target = target_tree.children[0].value
        return {"target": target, "statement_list": statement_list}
    def statement_list(self, tree):
        token = tree[0]
        statement_list_content = token.value
        return statement_list_content

def analyze(string_content: str):
    parse_tree = HighLevelStructure(file_contents=string_content).parse()
    return HLTransformer().transform(parse_tree)
