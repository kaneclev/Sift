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
class NoRawContentProvidedError(HighLevelTreeParseError):
    def __init__(self):
        super().__init__("generate()", "There was no raw content from the sift file passed to the generate() method.")

class TransformerParseError(InternalExceptionError):
    def __init__(self, method, reason):
        file = "HighLevelTree.py"
        cls = "HighLevelGrammar"
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
class BaseInternalActionError(InternalExceptionError):
    def __init__(self, method, reason):
        super().__init__(file="Action.py", cls="Action", method=method, reason=reason)


class MultipleActionDefinitionsError(BaseInternalActionError):
    def __init__(self, definitions: list[object]):
        reason = f"""
        Multiple 'Action' subclasses claimed the raw_content as their own:
            {print(str(definition) for definition in definitions)}
        """
        super().__init__( method="generate", reason=reason)

class NoDefinitionFoundError(BaseInternalActionError):
    def __init__(self, unclaimed_statement: str):
        reason = f"""
        The given content: {unclaimed_statement} was not identified as belonging to any Action subclass.
        """
        super().__init__(method="generate", reason=reason)

