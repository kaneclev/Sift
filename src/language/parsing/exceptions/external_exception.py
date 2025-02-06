class ExternalExceptionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MultipleDefinitionsError(ExternalExceptionError):
    def __init__(self, single_definition_feature, original_definition, offending_alternate_definitions):
        self.offending_feature = single_definition_feature
        self.original_definition = original_definition
        self.offending_alternate_definitions = offending_alternate_definitions
        super().__init__()
    def __str__(self):
        return f"Multiple definitions for '{self.offending_feature}'; \
                    \n\t Original Definition: {self.original_definition} \
                    \n\t New Definitions: {self.offending_alternate_definitions}"

class MultipleTargetListDefinitionsError(MultipleDefinitionsError):
    def __init__(self, original_definition: str, offending_alternate_definitions: list):
        offending_alternate_definitions_string = " | ".join(offending_alternate_definitions)
        formatted_offending_alternate_definitions_string = "Alternate definitions: ".join([offending_alternate_definitions_string])

        super().__init__("targets", original_definition, formatted_offending_alternate_definitions_string)
