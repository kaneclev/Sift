from lark import Lark, logger, Transformer
import logging
from Language.Structs.FilterTypes import FilterType
logger.setLevel(level=logging.DEBUG)
# TODO Finish implementing the action grammar.
action_grammar = """
action: filters assignment
filters: filter_keyword filter_parameters 
filter_keyword: /
assignment: /[\s^\r\n|\r|\n]+->[\s^\r\n|\r|\n]+([a-zA-Z_^;]+);/x



%import common.WS
%ignore WS
%ignore COMMENTS
"""


class ActionGrammar(Lark):
    def __init__(self, action: str):
        super().__init__(action_grammar, start='action', parser='lalr')
        self.contents = action
    def parse(self):
        return super().parse(self.contents)

class ActionTransformer(Transformer):
    pass

