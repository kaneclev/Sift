class InternalExceptionError(Exception):
    def __init__(self, file: str, cls: str, method: str, reason: str, *args):
        self.file = file
        self.cls = cls
        self.method = method
        self.reason = reason
        super().__init__(*args)
    def __str__(self):
        return f"Internal Error in file: {self.file} in class: {self.cls}: \n Offending method: {self.method} \n Reason: {self.reason}"

class InternalParseError(InternalExceptionError):
    pass
class HighLevelTreeParseError(InternalParseError):
    def __init__(self, method, reason, *args):
        file = "HighLevelTree.py"
        cls = "HighLevelTree"
        super().__init__(file, cls, method, reason, *args)

class TransformerParseError(InternalExceptionError):
    def __init__(self, method, reason, *args):
        file = "HighLevelTree.py"
        cls = "HLTransformers"
        super().__init__(file, cls, method, reason, *args)

class GenericGrammarError(InternalExceptionError):
    def __init__(self, method, reason, *args):
        file = "GenericGrammar.py"
        cls = "GenericGrammar"
        super().__init__(file, cls, method, reason, *args)
