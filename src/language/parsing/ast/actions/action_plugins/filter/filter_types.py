from language.parsing.ast.enums import HTMLPropertyType as FilterTypes


def match_filter_type(stmt: dict) -> FilterTypes:  # noqa: C901
    assert len(stmt.keys()) == 1, f"Too many keys in the filter statement: {stmt}"
    stmt_key = list(stmt.keys())[0]
    match stmt_key:
        case "attribute":
            return FilterTypes.ATTRIBUTE
        case "text":
            return FilterTypes.TEXT
        case "tag":
            return FilterTypes.TAG
