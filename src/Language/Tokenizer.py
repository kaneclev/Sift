import AST
import re

def tokenize(script):
    """Simple tokenizer for the Sift language."""
    token_specification = [
        ('TARGETS', r'targets:'),               # targets keyword
        ('ALIAS', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Alias (e.g., Ebay)
        ('STRING', r'"[^"]*"'),                # Strings (e.g., "www.ebay.com")
        ('COLON', r':'),                       # Colon
        ('COMMA', r','),                       # Comma
        ('LBRACE', r'\{'),                     # Left brace
        ('RBRACE', r'\}'),                     # Right brace
        ('SEMICOLON', r';'),                   # Semicolon
        ('PIPE', r'\|'),                       # Pipe
        ('CODENAME', r'codename'),             # codename keyword
        ('SIFT', r'sift'),                     # sift keyword
        ('FROM', r'from'),                     # from keyword
        ('WITH', r'with'),                     # with keyword
        ('AND', r'and'),                       # and keyword
        ('FILTER', r'[a-zA-Z]+'),              # General filter keywords
        ('LBRACKET', r'\['),                   # Left bracket
        ('RBRACKET', r'\]'),                   # Right bracket
        ('EQUALS', r'='),                      # Equals
        ('WHITESPACE', r'[ \t]+'),             # Skip whitespace
        ('NEWLINE', r'\n'),                    # Skip newlines
    ]
    token_re = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    get_token = re.compile(token_re).match
    print(token_re)
tokenize("a")
