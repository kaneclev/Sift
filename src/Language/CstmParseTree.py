import re
import SiftExcept
from enum import Enum
class Regex(Enum):
    VARIABLE = r'[a-zA-Z_]+'
    USER_DEFINED_STRING = r'[^"]*'

# TODO: make the SiftExcept accept context (line no, offending characters) to provide more descriptive exceptions.
def extract_raw_targets_as_list(contents) -> list: 
    targ_pat = re.compile(r'\s*targets:\s*\[([^\]]+)\]').pattern
    return re.findall(targ_pat, contents)

def group_target_pairs(contents) -> list[tuple]:
    raw_targs = extract_raw_targets_as_list(contents=contents)
    if len(raw_targs) > 1:
        raise SiftExcept.MultipleTargetsLists
    raw_targs = raw_targs[0]
    targ_pair_pattern = re.compile(rf'\s*({Regex.VARIABLE.value}):\s*"({Regex.USER_DEFINED_STRING.value})"').pattern
    groups = re.findall(targ_pair_pattern, raw_targs)
    return groups
    
def get_targets(contents) -> dict[str, str]:
    target_pairs = group_target_pairs(contents=contents)
    targets = {}
    for pair in target_pairs:
        var = pair[0]
        url = pair[1]
        targets[var] = url

    return targets


class ParseTree:
    def __init__(self, contents: str):
        self.targets = get_targets(contents=contents)
        print(self.targets)
        pass