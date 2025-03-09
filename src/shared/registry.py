from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Generic, Hashable, List, TypeVar, Union


class RegistryType(Enum):
    OP = auto()
    ACTION = auto()
    TARGET = auto()

registries: Dict[RegistryType, "Registry"] = {}
RegisteredItem = TypeVar("RegisteredItem")
RCollection = Union[List[RegisteredItem], Dict[Hashable, RegisteredItem]]

@dataclass
class Registry(Generic[RegisteredItem]):
    rtype: RegistryType
    registry: RCollection


def register(rtype: RegistryType, item: RegisteredItem, key: Hashable = "") -> None:
    is_mapping = True if key else False
    if rtype not in registries:
        if is_mapping:
            registries[rtype] = Registry(rtype=rtype, registry={})
        else:
            registries[rtype] = Registry(rtype=rtype, registry=[])
    if is_mapping:
        registries[rtype].registry[key] = item
        return
    registries[rtype].registry.append(item)
    return

def lookup(rtype: RegistryType, item: RegisteredItem = None, key: Hashable = "") -> Union[RegisteredItem, None]:
    if rtype not in registries:
        return None
    relevant_registry = registries[rtype]

    if isinstance(relevant_registry.registry, Dict):
        if not key:
            raise KeyError(f'Expected a key to look up an element in {rtype}, but recieved none.')
        return _find_in_registry_list(registry=relevant_registry, key=key)
    if isinstance(relevant_registry.registry, List):
        if not item:
            raise ValueError(f'Expected an item to find in registry {rtype}, but one was not passed.')
        return _find_in_registry_list(registry=relevant_registry, item=item)

def _find_in_registry_list(registry: Registry, key: Hashable = "", to_find: RegisteredItem = None) -> Union[RegisteredItem, None]:
    if isinstance(registry.registry, Dict):
        if key in registry.registry:
            return registry.registry[key]
        return None
    for item in registry.registry:
        if item == to_find:
            return item
    return None
