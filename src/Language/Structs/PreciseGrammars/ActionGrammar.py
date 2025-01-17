from lark import Lark, logger, Transformer
import logging
logger.setLevel(level=logging.DEBUG)
# TODO Finish implementing the action grammar.
action_grammar = """
start: action  

// The main action is a set of filters, then an assignment
action: filters assignment

// 1) FILTERS

filters: filter_keyword filter_parameters (bool_op filter_parameters)*

?filter_keyword: extract_where 
               | extract_from_previously_assigned

// a) "extract where" (two tokens: EXTRACT + WHERE)
extract_where: EXTRACT WHERE

// b) "extract from <LABEL> where"
extract_from_previously_assigned: EXTRACT FROM LABEL WHERE

// A single filter-parameter chunk: "tag" [qualifier] <filter>
filter_parameters: filter_type qualifier? filter

// Filter type: "tag", "attribute", or "text"
?filter_type: TAG | ATTRIBUTE | TEXT
TAG: "tag"
ATTRIBUTE: "attribute"
TEXT: "text"

// Optional qualifier: "contains" or "in"
?qualifier: CONTAINS | IN
CONTAINS: "contains"
IN: "in"

// The actual filter can be:
//   - key_value_filter (e.g. '"class":"search-result"')
//   - quoted_filter    (e.g. '"Ad"' or "'Ad'")
//   - list_of_quoted_filters (e.g. '["div","li"]')
?filter: key_value_filter 
       | quoted_filter 
       | list_of_quoted_filters

key_value_filter: quoted_filter ":" quoted_filter

// A quoted_filter can be single or double
quoted_filter: DOUBLE_QUOTED | SINGLE_QUOTED

// Double-quoted and single-quoted tokens
DOUBLE_QUOTED: /"[^"]*"/
SINGLE_QUOTED: /'[^']*'/

// bracketed list like ["div","li"]
list_of_quoted_filters: "[" [quoted_filter ("," quoted_filter)*] "]"

// 2) BOOLEAN OPERATORS

bool_op: AND 
       | OR 
       | AND_NOT 
       | OR_NOT

AND: "and"
OR: "or"
AND_NOT: "and not"
OR_NOT: "or not"

// 3) ASSIGNMENT

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

COMMENT: /\/\/[^\n]*/x
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
        filters, assignment = children
        return {
            'operation': filters,
            'assignment': assignment
        }

    def filters(self, children):
        # children = [filter_keyword, filter_parameters, (bool_op, filter_parameters)* ]
        #
        # We'll parse the first two, then handle pairs of (bool_op, filter_parameters).
        filter_keyword = children[0]
        first_filter_parameters = children[1]
        
        # The rest are in pairs: (bool_op, filter_parameters), (bool_op, filter_parameters)...
        bool_filters = []
        i = 2
        while i < len(children):
            op = children[i]        # bool_op
            fparams = children[i+1] # filter_parameters
            bool_filters.append((op, fparams))
            i += 2

        return {
            'filter_keyword': filter_keyword,
            'filters': [first_filter_parameters] + bool_filters
        }

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
    # filter_parameters
    #------------------------
    def filter_parameters(self, children):
        # children = [filter_type, (qualifier)?, filter]
        # Could be 2 or 3 children depending on qualifier presence
        if len(children) == 2:
            # no qualifier
            ftype, fltr = children
            qualifier = None
        else:
            ftype, qualifier, fltr = children
        
        return {
            'filter_type': ftype,      # 'tag'/'attribute'/'text'
            'qualifier': qualifier,    # 'contains'/'in' or None
            'filter': fltr            # This will be the result of key_value_filter, quoted_filter, or list_of_quoted_filters
        }

    #------------------------
    # filter_type tokens
    #------------------------
    def TAG(self, token):
        return str(token)  # "tag"

    def ATTRIBUTE(self, token):
        return str(token)  # "attribute"

    def TEXT(self, token):
        return str(token)  # "text"

    #------------------------
    # qualifier tokens
    #------------------------
    def CONTAINS(self, token):
        return str(token)  # "contains"

    def IN(self, token):
        return str(token)  # "in"

    #------------------------
    # filter
    #------------------------
    def key_value_filter(self, children):
        # children = [quoted_filter_1, quoted_filter_2]
        key = children[0]  # e.g. {"type": "quoted_filter", "value": "class"}
        val = children[1]  # e.g. {"type": "quoted_filter", "value": "search-result"}
        return {
            'type': 'key_value_filter',
            'key': key, 
            'value': val
        }

    def quoted_filter(self, children):
        # children = [ a SINGLE_QUOTED or DOUBLE_QUOTED token ]
        return children[0]  # we’ll transform SINGLE_QUOTED/DOUBLE_QUOTED below

    def list_of_quoted_filters(self, children):
        # children = [quoted_filter, quoted_filter, ...]
        # or might be empty if list is like []
        return {
            'type': 'list_of_quoted_filters',
            'items': children
        }

    #------------------------
    # quoted strings
    #------------------------
    def SINGLE_QUOTED(self, token):
        # e.g. "'some text'"
        text = str(token)
        # strip the quotes if desired
        unquoted = text[1:-1]  # remove the outer single quotes
        return {
            'type': 'quoted_string',
            'quote_style': 'single',
            'value': unquoted
        }

    def DOUBLE_QUOTED(self, token):
        # e.g. "\"some text\""
        text = str(token)
        # strip the quotes if desired
        unquoted = text[1:-1]  # remove the outer double quotes
        return {
            'type': 'quoted_string',
            'quote_style': 'double',
            'value': unquoted
        }

    #------------------------
    # bool_op
    #------------------------
    def bool_op(self, children):
    # children = [ Token('AND', 'and') ] (or OR, AND_NOT, etc.)
        return str(children[0])   # e.g. "and"
    def AND(self, token):
        return "and"

    def OR(self, token):
        return "or"

    def AND_NOT(self, token):
        return "and not"

    def OR_NOT(self, token):
        return "or not"

    #------------------------
    # assignment
    #------------------------
    def assignment(self, children):
        # children = [Token(ARROW, '->'), Token(LABEL, 'google_ads')] 
        # semicolon is matched but usually not part of children
        arrow, label_token = children
        return {
            'arrow': str(arrow),
            'label': str(label_token)
        }

    def ARROW(self, token):
        return str(token)  # "->"

    def LABEL(self, token):
        return str(token)  # e.g. "google_ads"

def analyze(string_content_to_analyze: str):
    ast = ActionGrammar(string_content_to_analyze).parse()
    return ActionTransformer().transform(ast)

