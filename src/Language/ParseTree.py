from lark import Lark, Transformer
sift_grammar = """
start: targets action_list

targets: "targets:" "[" target_items "]"
target_items: (VARIABLE ":" STRING) ("," VARIABLE ":" STRING)*

action_list: VARIABLE ":" "{" statement_list "}"
statement_list: statement*
statement: extract_operation

extract_operation: "extract where" (logical_or)? "->" VARIABLE ";"

logical_or: logical_and ("or" logical_and)*
logical_and: logical_operand ("and" logical_operand)*
logical_operand: "not" logical_operand
               | logical_group
               | condition

logical_group: "(" logical_or ")"

condition: tag_filter
         | attribute_filter
         | STRING

tag_filter: "tag" STRING
attribute_filter: "attribute" STRING ":" STRING
                | "attribute" STRING
                | "attribute" "{" attribute_map "}"

attribute_map: pair ("," pair)*
pair: STRING ":" (STRING | contains_operator)

contains_operator: "contains" STRING

VARIABLE: /[a-zA-Z_]+/
STRING: /"(?:\\\\.|[^"\\\\])*"/

%import common.WS
%ignore WS
"""



parser = Lark(sift_grammar, start='start', parser='lalr')
class SiftTransformer(Transformer):
    def start(self, args):
        """Transform the root start node."""
        targets, actions = args
        return {"targets": targets, "actions": actions}
    
    def targets(self, args):
        """Transform the targets section."""
        return dict(args)  # Flatten the targets directly
    
    def target_items(self, args):
        """Transform target items into a dictionary of key-value pairs."""
        # Ensure we are creating key-value pairs
        result = []
        for i in range(0, len(args), 2):
            result.append((args[i], args[i+1]))
        return result
    def action_list(self, args):
        """Transform the action list."""
        return args  # Return a list of actions
    
    def statement_list(self, args):
        """Transform a list of statements."""
        return args  # Return a list of statements directly
    
    def statement(self, args):
        """Transform a single statement."""
        filter_op = args[0] if len(args) > 2 else None
        return {"type": "extract", "filter": filter_op, "variable": args[-1]}
    
    def extract_operation(self, args):
        """Transform filter operations (with logical operators)."""
        if len(args) == 1:
            return args[0]
        return {"operator": args[1], "operands": [args[0], args[2]]}
    
    def condition(self, args):
        """Transform individual conditions."""
        if len(args) == 2 and args[0] == "tag":
            return {"type": "tag", "value": args[1]}
        elif len(args) == 3 and args[0] == "attribute":
            return {"type": "attribute", "name": args[1], "value": args[2]}
        elif len(args) == 2 and args[0] == "attribute":
            return {"type": "attribute", "name": args[1]}
        return {"type": "string", "value": args[0]}
    
    def VARIABLE(self, args):
        """Transform variables."""
        return str(args)
    
    def STRING(self, args):
        """Transform strings (removing quotes)."""
        return str(args)[1:-1]  # Remove quotes
