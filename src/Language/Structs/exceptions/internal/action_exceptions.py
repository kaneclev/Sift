from language.exceptions.internal_exception import InternalExceptionError

class BaseInternalActionError(InternalExceptionError):
    def __init__(self, method, reason):
        super().__init__(file="Action.py", cls="Action", method=method, reason=reason)


class MultipleActionDefinitionsError(BaseInternalActionError):
    def __init__(self, definitions: list[object]):
        reason = f"""
        Multiple 'Action' subclasses claimed the raw_content as their own:
            {print(str(definition) for definition in definitions)}
        """
        super().__init__( method="generate_action", reason=reason)

class NoDefinitionFoundError(BaseInternalActionError):
    def __init__(self, unclaimed_statement: str):
        reason = f"""
        The given content: {unclaimed_statement} was not identified as belonging to any Action subclass.
        """
        super().__init__(method="generate_action", reason=reason)

