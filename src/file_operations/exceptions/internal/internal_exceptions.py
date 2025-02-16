class BaseInternalFileError(Exception):
    """The base class for internal file-related exceptions.

    *Not to be raised directly; purely inheritable.*
    """
    def __init__(self, method: str, class_: str):
        """Initializes the BaseInternalFileError exception.

        Stores the method and class where the error occurred.

        Args:
            method (str): The method where the error was raised.
            class_ (str): The class containing the method.
        """
        self.method = method
        self.class_ = class_
        super().__init__()

class BadTypeError(BaseInternalFileError):
    """Raised when a method receives an argument of incorrect type.

    *Inherits from BaseInternalFileError.*
    """
    def __init__(self, method: str, class_: str, field: str, expected_type, given_type):
        """Creates a BadTypeError instance with type mismatch details.

        Args:
            method (str): Passed to BaseInternalFileError - method where error occurred
            class_ (str): Passed to BaseInternalFileError - class containing method
            field (str): Name of the argument with type mismatch
            expected_type (type): Expected type for the argument
            given_type (type): Actual type received
        """
        super().__init__(method=method, class_=class_)
        self.field = field
        self.expected_type = expected_type
        self.given_type = given_type

    def __str__(self):
        """Formats the type error message.

        Returns:
            str: Human-readable error message with type details
        """
        return f"Bad type passed to method: {self.method} in class: {self.class_}." \
            f"\nExpected type for field {self.field}: {self.expected_type}. Given type: {self.given_type}"

    def __repr__(self):
        """Official string representation of the exception.

        Returns:
            str: Technical representation for debugging
        """
        return f"{self.__class__.__name__}(method={self.method}, class_={self.class_})"

class ExceptionListError(BaseInternalFileError):
    """Raised when multiple exceptions need to be reported together.

    *Inherits from BaseInternalFileError.*
    """
    def __init__(self, exception_list: list[Exception]):
        """Creates an ExceptionListError instance.

        Args:
            exception_list (list[Exception]): Collection of exceptions that occurred
        """
        self.exception_list = exception_list
        super().__init__(method="", class_="")  # Empty strings to satisfy parent params

    def __str__(self):
        """Formats multiple exceptions into a consolidated message.

        Returns:
            str: Multi-line message listing all exceptions
        """
        exception_messages = "\n".join([f"{type(exc).__name__}: {exc}" for exc in self.exception_list])
        return f"Multiple exceptions occurred:\n{exception_messages}"
