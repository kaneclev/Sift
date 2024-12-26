import os
import sys
from typing import Union, Optional, Iterable, List, Dict
from SiftStructures.ReservedWords import ReservedWords
from enum import Enum
import re
class Regex(Enum):

    BRACKETS_CONTENT =  re.compile(r'\[\s*(.*?)\s*\]', re.DOTALL)
    BRACES_CONTENT = re.compile(r'\{\s*(.*?)\s*\}', re.DOTALL)
    TARGETS_KEYWORD = re.compile(r'(targets)[ ^\S\r\n\]+=\[ ^\S\r\n]+\[')
    # Get all the content between the targets list brackets.
    # NOTE!!!: This TARGETS_KEY_PAIR_VALUES must be used with the re.findall(TARGETS_LIST_CONTENT.value, <String to match>) to get all pairs.
    # TODO: Does this accept newlines between the colon and the url? Should it? 
    TARGETS_KEY_PAIR_VALUES = re.compile(r'([A-Za-z_]+)\s*:\s*"([^"]+)"')
    # NOTE: This does not validate that the term before the colon of the action block is a real 'target' that was registered in targets.
    TARGET_ACTION_BLOCK = re.compile(fr'\s*[a-zA-Z_]+:{BRACKETS_CONTENT.pattern}')
    REQUEST_CONTENT = re.compile(r'^\s*request([^;]+);', re.DOTALL)
    # captures the keywords just before the pipe statement
    PIPE_TO_CONTENT = re.compile(r'[a-zA-Z_^ ]+\|\s*([^;]+);')
    # Captures the 'codename' alias of a pipe statement. 
    PIPE_CODENAME = re.compile(r'\|[ ^\S\r\n]+codename[ ^\S\r\n]+([a-zA-Z_^;]+);')
    BRACE_CODENAME = re.compile(r'\}\s*\|\s*codename\s*([^;]+);')
    FILTER_AS_CODENAME = re.compile(r'\s*filter\s*([a-zA-Z_]+)\s*as\s*')
    # Use the BRACES_CONTENT to get the content after confirming the select keyword exists.
    SELECT_KEYWORD = re.compile(r'^\s*select\s*\{')
    SELECT_TAGS = re.compile(r'''
        (tags\s*(?: # start capturing the entire statement, then use (?: to say 'dont actually capture it but consider these or-options seperate from the original tags term
        "[^"]*" # quotes case
        |\{[^}]*\} # braces case
        |\[[^\]]*\] # brackets case
        )) # end the capture
        [ ^\S\r\n]+ # require one or more spaces at the end or a pipe symbol.
        |\| 
        ''', re.VERBOSE)
    SELECT_ATTRIBUTES = re.compile(r'''
        (attributes\s*(?: # start capturing the entire statement, then use (?: to say 'dont actually capture it but consider these or-options seperate from the original tags term
        "[^"]*" # quotes case
        |\{[^}]*\} # braces case
        |\[[^\]]*\] # brackets case
        )) # end the capture
        ''', re.VERBOSE)
    SELECT_TEXT = re.compile(r'''
        (text\s*(?: # start capturing the entire statement, then use (?: to say 'dont actually capture it but consider these or-options seperate from the original tags term
        "[^"]*" # quotes case
        |\{[^}]*\} # braces case
        |\[[^\]]*\] # brackets case
        )) # end the capture
        ''', re.VERBOSE)
    # SELECT_STATEMENTS is expected to be used on the result of the BRACKETS_CONTENT regex applied to the entire 'select' block
    SELECT_STATEMENTS = re.compile(fr'\s*([a-zA-Z_]:[ ^\S\r\n]+[{SELECT_ATTRIBUTES}|{SELECT_TAGS}|{SELECT_TEXT}\s*(?:with|)\s*]+[^;]+;)')

class SiftFile:#
    def __init__(self, path: str):
        self.lines: str = []
        self.path = path
        path_problems: list[Exception] = SiftFile.validate_path_adherence(path=path)
        if len(path_problems) > 0:
            for issue in path_problems:
                sys.stderr.write(f'Cannot read in file: {issue}\n')
            exit(-1)
        self.lines = Parse.chop_file_into_lines(path)
        pass

    def get_file_as_array(self):
        return self.lines
    def get_file_as_string(self):
        return ''.join(self.lines)
    
    
    @staticmethod
    def validate_path_adherence(path: str) -> list[Exception]:
        issues: list[Exception] = []
        if not os.path.exists(path):
            issues.append(FileNotFoundError(f'{path} not found.'))
        if os.path.basename(path).split('.')[1] != "sift" or len(os.path.basename(path).split('.')) != 2:
            issues.append(FileNotFoundError(f'The given file has an incorrect extension. Expected ".sift", recieved: {os.path.basename(path)}'))
        return issues
    
    
class Parse:
    def chop_file_into_lines(path: str):
        collected_lines = []
        with open(path, 'r') as file:
            for line in file:
                collected_lines.append(line)
        return collected_lines

a = SiftFile(r'C:\Users\Kane\projects\Sift\siftscripts\example.sift')
print(a.get_file_as_string())
