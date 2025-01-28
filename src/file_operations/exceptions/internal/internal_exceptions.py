class BaseInternalFileError(Exception):
    def __init__(self, method: str, class_: str):
        self.method = method
        self.class_ = class_
        super().__init__()

class BadTypeError(BaseInternalFileError):
    def __init__(self, method: str, class_: str, field: str, expected_type, given_type):
        super().__init__(method=method, class_=class_)
        self.field = field
        self.expected_type = expected_type
        self.given_type = given_type
    def __str__(self):
        return f"Bad type passed to method: {self.method} in class: {self.class_}." \
            f"\nExpected type for field {self.field}: {self.expected_type}. Given type: {self.given_type}"
    def __repr__(self):
        return f"{self.__class__.__name__}(method={self.method}, class_={self.class_})"

class ExceptionListError(BaseInternalFileError):
    def __init__(self, exception_list: list[Exception]):
        super().__init__()
        self.exception_list = exception_list
    def __str__(self):
        # Format all exceptions as a readable message
        exception_messages = "\n".join([f"{type(exc).__name__}: {exc}" for exc in self.exception_list])
        return f"Multiple exceptions occurred:\n{exception_messages}"



