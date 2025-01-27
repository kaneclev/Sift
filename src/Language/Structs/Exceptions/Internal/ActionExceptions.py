from Language.Exceptions.InternalException import InternalException

class BaseInternalActionException(InternalException):
    def __init__(self, method, reason, *args):
        super().__init__(file="Action.py", cls="Action", method=method, reason=reason, *args)


class MultipleActionDefinitions(BaseInternalActionException):
    def __init__(self, definitions: list[object], *args):
        reason = f"""
        Multiple 'Action' subclasses claimed the raw_content as their own: 
            {print(str(definition) for definition in definitions)}
        """
        super().__init__( method="generate_action", reason=reason, *args)

class NoDefinitionFound(BaseInternalActionException):
    def __init__(self, unclaimed_statement: str, *args):
        reason = f"""
        The given content: {unclaimed_statement} was not identified as belonging to any Action subclass.        
        """
        super().__init__(method="generate_action", reason=reason *args)