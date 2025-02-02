from enum import Enum


class FilterTypes(Enum):
    TEXT = "text"
    TEXT_CONTAINS = "text contains"
    ATTRIBUTE = "attribute"
    ATTRIBUTE_CONTAINS = "attribute contains"
    TAG = "tag"
    UNKNOWN = ""

def match_filter_type(stmt: dict) -> FilterTypes:
    assert len(stmt.keys()) == 1, f"Too many keys in the filter statement: {stmt}"
    stmt_key = list(stmt.keys())
    if stmt_key == "attribute":
        # Then it will be a list, where the first part is the attrib name, the second entry is the attrib value
        if isinstance(stmt[stmt_key], list):
            if len(stmt[stmt_key]) == 2:
                if isinstance(stmt[stmt_key][0], str) and isinstance(stmt[stmt_key][1], str):

                    return FilterTypes.ATTRIBUTE
                elif isinstance(stmt[stmt_key][0], str) and isinstance(stmt[stmt_key][1], dict):
                    return FilterTypes.ATTRIBUTE_CONTAINS
                else:
                    return FilterTypes.UNKNOWN
            else:
                return FilterTypes.UNKNOWN
        else:
            return FilterTypes.UNKNOWN
    if stmt_key == "text":
        if isinstance(stmt[stmt_key], list):
            return FilterTypes.TEXT
        elif isinstance(stmt[stmt_key], dict):
            if list(stmt[stmt_key].keys())[0] == "contains_text":
                return FilterTypes.TEXT_CONTAINS
        else:
            return FilterTypes.UNKNOWN
