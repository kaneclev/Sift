import os
import sys
from typing import Union, Optional, Iterable, List, Dict
class SiftFile:
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