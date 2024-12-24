import os
import sys
from typing import Union, Optional, Iterable, List, Dict
class SiftFile:
    def __init__(self, path: str):
        path_problems: list[Exception] = SiftFile.validate_path_adherence(path=path)

        if len(path_problems) > 0:
            for issue in path_problems:
                sys.stderr.write(f'Cannot read in file: {issue}')
                exit(-1)
            
        
        pass

    @staticmethod
    def validate_path_adherence(path: str) -> list[Exception]:
        issues: list[Exception] = []
        if not os.path.exists(path):
            issues.append(FileNotFoundError(f'{path} not found.'))
        if os.path.basename(path).split('.')[1] != ".sift" or len(os.path.basename(path).split('.')) != 2:
            issues.append(FileNotFoundError(f'The given file has an incorrect extension. Expected ".sift", recieved: {os.path.basename(path)}'))
        return issues
a = SiftFile('.aaa')