from language.parsing.utils import GrammarContainer, SyntaxProcessor

#######################
## Grammars ###########
#######################

FILTER = GrammarContainer(start="filter_expr")
FILTER.production_map = {
    # Top-level
    "?filter_expr": "or_expr",

    # Keep original left-recursive structure to maintain transformations
    "?or_expr": "and_expr | or_expr \"or\" and_expr -> or_operator",

    "?and_expr": "not_expr | and_expr \"and\" not_expr -> and_operator",

    "?not_expr": "\"not\" not_expr -> not_operator | atom",

    "?atom": "\"(\" filter_expr \")\" -> group | filter_item",

    # Order from most specific to least specific
    "?filter_item": "attribute_filter | tag_filter | text_filter",

    # Original tag_filter preserved
    "tag_filter":
        "\"tag\" WS? (ESCAPED_STRING | options) -> tag",

    # Original attribute_filter preserved
    "attribute_filter":
        "\"attribute\" WS? (pair | \"[\" WS? pair (WS? \",\" WS? pair)* WS? \"]\") -> attribute",

    # Original attribute_value_expr preserved
    "?attribute_value_expr":
        "contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value",

    # Original pair preserved
    "pair":
        "(ESCAPED_STRING | wildcard_value) WS? \":\" WS? "
        "(contains_attribute"
        "| options"
        "| ESCAPED_STRING"
        "| wildcard_value)",

    # Original text_filter preserved
    "text_filter":
        "\"text\" WS? (contains_text | ESCAPED_STRING | options) -> text",

    # Original rules preserved
    "contains_attribute":
        "\"contains\" WS? (ESCAPED_STRING | options)",

    "contains_text":
        "\"contains\" WS? (ESCAPED_STRING | options)",

    "options":
        "\"[\" WS? ESCAPED_STRING (WS? \",\" WS? ESCAPED_STRING)* WS? \"]\"",

    "wildcard_value":
        "\"any\""
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

ACTION_BLOCK = GrammarContainer(start="block")
ACTION_BLOCK.production_map = {
    "block": "_START (action)+ _END",
    "_START": r"/\s*\{\s*/",
    "_END": r"/\s*\}\s*/",
    "?action": r"/\s*[^;]+;/"
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


HIGH_LEVEL = GrammarContainer(start="script")
HIGH_LEVEL.production_map = {
    "script": "target_list (action_list)?",
    "target_list": "_TARGETS~1 TL_REGEX_DEFINITION~1",
    "_TARGETS": r"/targets\s*=\s*/",
    "TL_REGEX_DEFINITION": r"/\[[^\]]+\]/",
    "action_list": "action+",
    "action": "target statement_list",
    "target": "SOME_TARGET",
    "SOME_TARGET": r"/[a-zA-Z_^:]+:[\s^\r\n|\r|\n]+/x",
    "statement_list": r"/\{[^\}]*\}/"
}


###############################
## Grammar Class Definitions ##
###############################

class FilterGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(FILTER, content)
    def analyze(self):
        dict_filter_representation = super().analyze()
        return dict_filter_representation

class ActionBlockGrammar(SyntaxProcessor):
    def __init__(self, content):
        super().__init__(ACTION_BLOCK, content)
        pass
    def analyze(self):
        generic_dict_representation = super().analyze()
        action_statement_list = []
        for action_stmt in generic_dict_representation['block']:
            action_statement_list.append(action_stmt)
        return action_statement_list

class HighLevelGrammar(SyntaxProcessor):
    """ Defines an interactor class for HighLevelTree to use.
    Inherits from SyntaxProcessor, who handles the parsing of a given Sift grammar.
    """
    def __init__(self, content):
        """ Initializes the parent SyntaxProcessor for use by HighLevelTree.
        HighLevelTree provides the content-to-parse (sift file content) which
        is then turned into a high-level, mostly raw, intermediate representation
        of the provided Sift script.

        Args:
            content (str): The content of the Sift script file.
        """
        super().__init__(HIGH_LEVEL, content)
