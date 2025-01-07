class ExceptionList(Exception):
    def __init__(self, exception_list: list[Exception], *args):
        super().__init__(*args)
        self.exception_list = exception_list
    def __str__(self):
        # Format all exceptions as a readable message
        exception_messages = "\n".join([f"{type(exc).__name__}: {exc}" for exc in self.exception_list])
        return f"Multiple exceptions occurred:\n{exception_messages}"

class BadArgumentTypeException(Exception):
    def __init__(self, argument, *args):
        super().__init__(*args)
        self.bad_type = type(argument)
    def __str__(self):
        return(f"Expected path of type string or Path, recieved type: {self.bad_type}")

class HighLevelStructureTreeException(Exception):
    def __init__(self, string_tree: str, why: str, *args):
        self.bad_tree = string_tree
        self.why = why
        super().__init__(*args)
    def __str__(self):
        return(f"There was an issue with the High-Level structure tree. \n Cause: {self.why} \n Offending Tree: {self.bad_tree}")
"""TODO
Create child exceptions for different kinds of high-level structure tree issues.
"""
