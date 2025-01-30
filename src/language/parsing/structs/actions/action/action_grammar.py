import logging

from lark import Lark, Transformer, logger

logger.setLevel(level=logging.DEBUG)
action_grammar = """
start: action

// The main action is a set of filters, then an assignment
action: filters assignment

// 1) FILTERS

filters: filter_keyword filter_statement

?filter_keyword: extract_where
               | extract_from_previously_assigned

// a) "extract where" (two tokens: EXTRACT + WHERE)
extract_where: EXTRACT WHERE

// b) "extract from <LABEL> where"
extract_from_previously_assigned: EXTRACT FROM LABEL WHERE

filter_statement: FILTER_CONTENT

// A terminal that captures EVERYTHING until we see -> (but doesn't consume ->)
FILTER_CONTENT: /([^-]|-(?!>))+/s

assignment: ARROW LABEL ";"

// e.g. -> google_ads;
ARROW: "->"

// The name/label on the right-hand side, e.g. google_ads
LABEL: /[a-zA-Z_]+/

// 4) KEYWORDS

EXTRACT: "extract"
FROM: "from"
WHERE: "where"

// 5) COMMENTS, WHITESPACE, ETC.

COMMENT: /\\/\\/[^\n]*/x
%ignore COMMENT
%import common.WS
%ignore WS



"""


class ActionGrammar(Lark):
    def __init__(self, action: str):
        super().__init__(action_grammar, start='start', parser='lalr')
        self.contents = action
    def parse(self):
        return super().parse(self.contents)

class ActionTransformer(Transformer):
    """Transform the parse tree into a dict-based structure."""

    def start(self, children):
        # There's usually just one 'action' child
        # Return that directly or wrap it in a dict
        return children[0]

    def action(self, children):
        # children = [filters, assignment]
        action_dict = {}
        op_dict, filters = children[0].children
        operation = op_dict['type']
        action_dict['operation'] = operation
        if 'label' in op_dict:
            action_dict['label'] = op_dict['label']
        action_dict['filter_statement'] = filters
        assignment = children[1]
        action_dict['assignment'] = assignment
        return action_dict

    def filter_statement(self, children):
        # The parser rule is: filter_statement: FILTER_CONTENT
        # So children should be [Token(FILTER_CONTENT, 'the captured text')]
        content_token = children[0]
        return str(content_token)

    #------------------------
    # filter_keyword rules
    #------------------------
    def extract_where(self, children):
        # children = [ Token(EXTRACT, 'extract'), Token(WHERE, 'where') ]
        return {
            'type': 'extract_where'
        }

    def extract_from_previously_assigned(self, children):
        # children = [Token(EXTRACT, 'extract'), Token(FROM, 'from'), Token(LABEL, 'google_results'), Token(WHERE, 'where')]
        label_token = children[2]
        return {
            'type': 'extract_from',
            'label': str(label_token)  # e.g. "google_results"
        }


    #------------------------
    # assignment
    #------------------------
    def assignment(self, children):
        # children = [Token(ARROW, '->'), Token(LABEL, 'google_ads')]
        # semicolon is matched but usually not part of children
        arrow, label_token = children
        return str(label_token)

    def ARROW(self, token):  # noqa: N802 -> lark grammar requirement
        return str(token)  # "->"

    def LABEL(self, token): # noqa: N802 -> lark grammar requirement
        return str(token)  # e.g. "google_ads"

def analyze(string_content_to_analyze: str):
    ast = ActionGrammar(string_content_to_analyze).parse()
    return ActionTransformer().transform(ast)

