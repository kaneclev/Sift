from language.grammar_container import GrammarContainer
from language.parsing.grammar_transformer_interface import SyntaxProcessor

action_block_grammar = GrammarContainer(start="block")
action_block_grammar.production_map = {
    "block": "_START (action)+ _END",
    "_START": r"/\s*\{\s*/",
    "_END": r"/\s*\}\s*/",
    "?action": r"/\s*[^;]+;/"
}


class ActionBlockGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(action_block_grammar, content)
        pass
    def analyze(self):
        generic_dict_representation = super().analyze()
        action_statement_list = []
        for action_stmt in generic_dict_representation['block']:
            action_statement_list.append(action_stmt)
        return action_statement_list

