from typing import List
from api.language_api.script_representations import Issue
class BaseCompilerException(Exception):
    def __init__(self) -> None:
        ...

class UnparsableScriptException(BaseCompilerException):
    def __init__(self, reasons: List[Issue]) -> None:
        # Convert the list of Issue objects into something digestible to be shown to the console.
        self.reasons: str = ""
        for reason in reasons:
            self.reasons += (str(reason) + " \n")
        super().__init__()
        
    def __str__(self) -> str:
        return f"Cannot parse provided sift script: {self.reasons}"