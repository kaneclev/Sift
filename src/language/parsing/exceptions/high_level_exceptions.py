class HLGrammarError(Exception):
    def __init__(self, offending_rule: str, *args):
        self.offending_rule = offending_rule
        super().__init__(*args)


    def __str__(self):
        exception_type = self.__class__.__name__
        return f"{exception_type} occurred: {self.offending_rule}"

class IncompleteTargetListError(HLGrammarError):
    def __init__(self, bad_target_list: str,  *args):
        offending_rule = f"Incomplete Target List definition: {bad_target_list}"
        super().__init__(offending_rule, *args)

class NonExistentTargetListError(HLGrammarError):
    def __init__(self, *args):
        offending_rule = "No targets list found; there must be at least one target and its respective URL defined for Sift to act upon."
        super().__init__(offending_rule, *args)
