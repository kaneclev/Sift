from typing import Dict


class ExternalExceptionError(Exception):
    """Base class for external-facing exception hierarchy.

    *Not to be raised directly; serves as foundation for specific error types.*
    """
    def __init__(self, *args):
        """Initializes external exception with flexible arguments.

        Args:
            *args: Variable length argument list passed to base Exception class
        """
        super().__init__(*args)

class MultipleDefinitionsError(ExternalExceptionError):
    """Raised when multiple conflicting definitions exist for a feature.

    *Inherits from ExternalExceptionError.*
    """
    def __init__(self, single_definition_feature: str, original_definition: str,
                 offending_alternate_definitions: list):
        """Records definition conflict details.

        Args:
            single_definition_feature (str): Name of the multiply-defined feature
            original_definition (str): First/valid definition encountered
            offending_alternate_definitions (list): Conflicting alternative definitions
        """
        self.offending_feature = single_definition_feature
        self.original_definition = original_definition
        self.offending_alternate_definitions = offending_alternate_definitions
        super().__init__()

    def __str__(self) -> str:
        """Formats definition conflict message.

        Returns:
            str: Structured error message showing original vs alternatives
        """
        return f"Multiple definitions for '{self.offending_feature}'; \
                    \n\t Original Definition: {self.original_definition} \
                    \n\t New Definitions: {self.offending_alternate_definitions}"

class MultipleTargetListDefinitionsError(MultipleDefinitionsError):
    """Specialized error for conflicting 'targets' list definitions.

    *Inherits from MultipleDefinitionsError.*
    """
    def __init__(self, original_definition: str, offending_alternate_definitions: list):
        """Processes target list conflicts into readable format.

        Args:
            original_definition (str): Valid target list definition
            offending_alternate_definitions (list): Conflicting target definitions
        """
        # Convert list to pipe-separated string
        offending_alternate_definitions_string = " | ".join(offending_alternate_definitions)
        # Add context prefix to alternative definitions
        formatted_offending_alternate_definitions_string = "Alternate definitions: ".join(
            [offending_alternate_definitions_string]
        )

        super().__init__(
            "targets",
            original_definition,
            formatted_offending_alternate_definitions_string
        )
class SyntaxError(ExternalExceptionError):
    def __init__(self, context: Dict):
        self.offense = context["offense"]
        self.col = context["col"]
        self.line = context["line"]
        self.expected: Dict[str, str] = context["expected"]
        self.pretty_expected = []

        for exp_rule, _ in self.expected.items():
            self.pretty_expected.append(f"'{exp_rule}'")

        self.expected = " ".join(self.pretty_expected)

    def __str__(self):
        reason = [
            f"Unexpected values: '{self.offense}' at line {self.line}, column {self.col}. "
            f"Expected one of: {self.expected}"
        ]
        return "\n".join(reason)

