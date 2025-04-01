#! TODO: Refactor
class InternalExceptionError(Exception):
    """Base class for internal system exception hierarchy.

    *Not to be raised directly; serves as foundation for specific error types.*
    """
    def __init__(self, file: str, cls: str, method: str, reason: str):
        """Initializes internal exception with contextual information.

        Args:
            file (str): Source file where error originated
            cls (str): Class containing the error location
            method (str): Method where error was detected
            reason (str): Technical description of failure cause
        """
        self.file = file
        self.cls = cls
        self.method = method
        self.reason = reason
        super().__init__()

    def __str__(self):
        """Formats complete error context for display.

        Returns:
            str: Structured error message with debugging details
        """
        return f"Internal Error in file: {self.file} in class: {self.cls}: \n Offending method: {self.method} \n Reason: {self.reason}"

class InternalParseError(InternalExceptionError):
    """Base class for parsing-related errors in internal components.

    *Inherits from InternalExceptionError.*
    """

class HighLevelTreeParseError(InternalParseError):
    """Indicates parsing failures specific to HighLevelTree operations.

    *Inherits from InternalParseError.*
    """
    def __init__(self, method: str, reason: str):
        """Creates error instance with predefined file/class context.

        Args:
            method (str): Method in HighLevelTree where failure occurred
            reason (str): Technical explanation of parsing failure
        """
        file = "HighLevelTree.py"
        cls = "HighLevelTree"
        super().__init__(file, cls, method, reason)

class NoRawContentProvidedError(HighLevelTreeParseError):
    """Raised when generate() method lacks required input content.

    *Inherits from HighLevelTreeParseError.*
    """
    def __init__(self):
        """Initializes error with predefined generate() method context."""
        super().__init__("generate()", "There was no raw content from the sift file passed to the generate() method.")

class TransformerParseError(InternalExceptionError):
    """Indicates failures in grammar transformation processes.

    *Inherits from InternalExceptionError.*
    """
    def __init__(self, method: str, reason: str):
        """Creates error instance with transformer-specific context.

        Args:
            method (str): Method in HighLevelGrammar where failure occurred
            reason (str): Detailed explanation of transformation failure
        """
        file = "HighLevelTree.py"
        cls = "HighLevelGrammar"
        super().__init__(file, cls, method, reason)

class GrammarHandlerError(InternalExceptionError):
    """Signals generic grammar handling failures.

    *Inherits from InternalExceptionError.*
    """
    def __init__(self, method: str, reason: str):
        """Initializes error with GenericGrammar handler context.

        Args:
            method (str): Problematic method in GenericGrammar
            reason (str): Specific handler failure description
        """
        file = "transformer.py"
        cls = "GenericGrammar"
        super().__init__(file, cls, method, reason)

class GrammarContainerError(InternalExceptionError):
    """Indicates issues with grammar container configuration.

    *Inherits from InternalExceptionError.*
    """
    def __init__(self, method: str, reason: str):
        """Creates grammar container error instance.

        Args:
            method (str): Method in GrammarContainer causing failure
            reason (str): Detailed container configuration issue
        """
        file = "grammar_container.py"
        cls = "GrammarContainer"
        super().__init__(file, cls, method, reason)

class NoStartRuleError(GrammarContainerError):
    """Raised when specified start rule doesn't exist in production map.

    *Inherits from GrammarContainerError.*
    """
    def __init__(self, method: str, bad_start_rule: str):
        """Initializes error with missing rule details.

        Args:
            method (str): Method attempting to use invalid start rule
            bad_start_rule (str): Name of undefined rule being referenced
        """
        reason = f"The provided rule: {bad_start_rule} is not defined in the production map."
        super().__init__(method, reason)

class BaseInternalActionError(InternalExceptionError):
    """Foundation for action-related processing errors.

    *Inherits from InternalExceptionError.*
    """
    def __init__(self, method: str, reason: str):
        """Creates base action error with predefined context.

        Args:
            method (str): Action method where failure occurred
            reason (str): General description of action failure
        """
        super().__init__(file="Action.py", cls="Action", method=method, reason=reason)

class MultipleActionDefinitionsError(BaseInternalActionError):
    """Indicates conflicting ownership claims for raw content.

    *Inherits from BaseInternalActionError.*
    """
    def __init__(self, definitions: list[object]):
        """Documents multiple conflicting action definitions.

        Args:
            definitions (list[object]): Collection of competing Action subclasses
        """
        reason = f"""
        Multiple 'Action' subclasses claimed the raw_content as their own:
            {', '.join(str(definition) for definition in definitions)}
        """
        super().__init__(method="generate", reason=reason)

class NoDefinitionFoundError(BaseInternalActionError):
    """Raised when content can't be associated with any Action.

    *Inherits from BaseInternalActionError.*
    """
    def __init__(self, unclaimed_statement: str):
        """Records unprocessed content details.

        Args:
            unclaimed_statement (str): Content that failed classification
        """
        reason = f"""
        The given content: {unclaimed_statement} was not identified as belonging to any Action subclass.
        """
        super().__init__(method="generate", reason=reason)

class IncorrectContentForPluginError(BaseInternalActionError):
    def __init__(self, plugin: str):
        reason = f"The content passed to generate() is unexpected for the {plugin} plugin."
        super().__init__(method="generate", reason=reason)


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
