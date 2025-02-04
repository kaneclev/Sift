from enum import Enum


class FilterTypes(Enum):
    TEXT = "text"
    TEXT_CONTAINS = "text contains"
    ATTRIBUTE = "attribute"
    ATTRIBUTE_CONTAINS = "attribute contains"
    TAG = "tag"
    UNKNOWN = ""

def match_filter_type(stmt: dict) -> FilterTypes:  # noqa: C901
    assert len(stmt.keys()) == 1, f"Too many keys in the filter statement: {stmt}"
    stmt_key = list(stmt.keys())[0]
    match stmt_key:
        case "attribute":
            for value in stmt[stmt_key]:
                if isinstance(value, str):
                    return FilterTypes.ATTRIBUTE
                if isinstance(value, dict):
                    attribute_value_keys = list(value.keys())
                    if any("contains" in key for key in attribute_value_keys):
                        return FilterTypes.ATTRIBUTE_CONTAINS
                    if any("pair" in key for key in attribute_value_keys):
                        return FilterTypes.ATTRIBUTE
            return FilterTypes.UNKNOWN
        case "text":
            for value in stmt[stmt_key]:
                if isinstance(value, str):
                    return FilterTypes.TEXT
                if isinstance(value, dict):
                    text_value_keys = list(value.keys())
                    if any("contains" in key for key in text_value_keys):
                        return FilterTypes.TEXT_CONTAINS
            return FilterTypes.UNKNOWN
        case "tag":
            return FilterTypes.TAG
        case _:
            print(f'Is this a tag filter? No case for it yet in filter_types.py: {stmt}')
