import logging

from lark import Lark, Transformer, logger

logger.setLevel(level=logging.DEBUG)
action_block_grammar = """
block:  _START (action)+ _END
_START: /\\s*\\{\\s*/
_END:  /\\s*\\}\\s*/
action: /\\s*[^;]+;/
COMMENTS: /\\/\\/[^\r\n|\r|\n]+/x

%import common.WS
%ignore COMMENTS
%ignore WS
"""


class ActionBlockGrammar(Lark):
    def __init__(self, action_block: str):
        super().__init__(action_block_grammar, start='block', parser='lalr')
        self.contents = action_block
    def parse(self):
        return super().parse(self.contents)

class ActionBlockTransformer(Transformer):
    def block(self, content):
        return content
    def action(self,content):
        token = content[0]
        action_line = token.value
        return action_line

def analyze(content: str):
    parsed = ActionBlockGrammar(content).parse()
    return ActionBlockTransformer().transform(parsed)
