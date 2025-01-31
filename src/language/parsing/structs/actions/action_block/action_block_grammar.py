from language.parsing.grammar_transformer_interface import SyntaxProcessor

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

class ActionBlockGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(action_block_grammar, 'block', content)
        pass
    def analyze(self):
        generic_dict_representation = super().analyze()
        action_statement_list = []
        for action_dict in generic_dict_representation['block']:
            action_statement_list.append(action_dict['action'])
        return action_statement_list

