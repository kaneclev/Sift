from enum import Enum
class SiftTypes(Enum):
    TARGET = "Target"
    CODENAME = "Codename"
    ACTION_BLOCK = "ActionBlock"
    REQUEST = "Request"
    FILTER_BLOCK = "FilterBlock"
    FILTER_RULE = "Filter"
    ATTRIBUTE = "Attribute"
    TAG = "Tag"
    SELECT_BLOCK = "SelectBlock"
    URL = "Url",
    TARGET_BLOCK = "TargetBlock"

class SiftType:
    def __init__(self, sift_type: SiftTypes):
        if not isinstance(sift_type, SiftTypes):
            raise TypeError(f"Base class constructor was passed an object of type {type(sift_type)} when it was expected to be of type SiftTypes")
        self.type = sift_type
        pass
    def type(self):
        return self.type.value

