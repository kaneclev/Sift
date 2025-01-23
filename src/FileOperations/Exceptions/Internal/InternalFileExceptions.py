class BaseInternalFileException(Exception):
    def __init__(self, method: str, class_: str, *args):
        self.method = method
        self.class_ = class_
        super().__init__(*args)

class BadType(BaseInternalFileException):
    def __init__(self, method: str, class_: str, field: str, expected_type, given_type, *args):
        super().__init__(method=method, class_=class_, *args)
        self.field = field
        self.expected_type = expected_type
        self.given_type = given_type
    def __str__(self):
        return f"Bad type passed to method: {self.method} in class: {self._class}." \
            f"\nExpected type for field {self.field}: {self.expected_type}. Given type: {self.given_type}"
    
class ExceptionList(BaseInternalFileException):
    def __init__(self, exception_list: list[Exception], *args):
        super().__init__(*args)
        self.exception_list = exception_list
    def __str__(self):
        # Format all exceptions as a readable message
        exception_messages = "\n".join([f"{type(exc).__name__}: {exc}" for exc in self.exception_list])
        return f"Multiple exceptions occurred:\n{exception_messages}"


