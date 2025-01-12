class SiftSyntaxError(Exception):
    def __init__(self, violating_content: dict[int, str], *args):
        for line_no, text in violating_content.items():
            assert isinstance(line_no, int), (
                f"The violating_content dict passed to the SyntaxError base class was incorrect; "
                f"expected type 'int', received type {type(line_no)} for the line number."
            )
            assert isinstance(text, str), (
                f"The violating_content dict passed to the SyntaxError base class was incorrect; "
                f"expected type 'str', received type {type(text)} for the text associated with line: {line_no}."
            )
        self.content = violating_content
        super().__init__(*args)

    def __str__(self):
        # Generate the list of line numbers and offending text
        violations = "\n".join(
            [f"Line {line_no}: {text}" for line_no, text in self.content.items()]
        )
        # Get the class name of the current exception (child class)
        exception_type = self.__class__.__name__
        # Return the formatted string
        return f"{exception_type} occurred:\n{violations}"

        
class MultipleTargetsDefinitions(SiftSyntaxError):
    pass

class IncorrectTargetsDefinition(SiftSyntaxError):
    pass

class InvalidCharactersInVariable(SiftSyntaxError):
    pass