class MultipleTargetsLists(Exception):
    def __init__(self, message="There are multiple definitions of the 'targets' list. "):
        super().__init__(message)
        self.message = message