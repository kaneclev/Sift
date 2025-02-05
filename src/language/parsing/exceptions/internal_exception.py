class InternalExceptionError(Exception):
    def __init__(self, file: str, cls: str, method: str, reason: str):
        self.file = file
        self.cls = cls
        self.method = method
        self.reason = reason
        super().__init__()
    def __str__(self):
        return f"Internal Error in file: {self.file} in class: {self.cls}: \n Offending method: {self.method} \n Reason: {self.reason}"

class InternalParseError(InternalExceptionError):
    pass
class HighLevelTreeParseError(InternalParseError):
    def __init__(self, method, reason):
        file = "HighLevelTree.py"
        cls = "HighLevelTree"
        super().__init__(file, cls, method, reason)

class TransformerParseError(InternalExceptionError):
    def __init__(self, method, reason):
        file = "HighLevelTree.py"
        cls = "HLTransformers"
        super().__init__(file, cls, method, reason)

class GrammarHandlerError(InternalExceptionError):
    def __init__(self, method, reason):
        file = "transformer.py"
        cls = "GenericGrammar"
        super().__init__(file, cls, method, reason)

class GrammarContainerError(InternalExceptionError):
    def __init__(self, method, reason):
        file = "grammar_container.py"
        cls = "GrammarContainer"
        super().__init__(file, cls, method, reason)

class NoStartRuleError(GrammarContainerError):
    def __init__(self, method, bad_start_rule):
        reason = f"The provided rule: {bad_start_rule} is not defined in the production map."
        super().__init__(method, reason)
