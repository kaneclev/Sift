from dataclasses import dataclass
from enum import Enum, auto


class ComTypes(Enum):
    FILESYS = auto()
class MsgType(Enum):
    JSON = auto()
class Recievers(Enum):
    REQUEST_MANAGER = auto()
@dataclass
class IPCOptions:
    com_type: ComTypes
    msg_type: MsgType
    recipient: Recievers
    def __post_init__(self):
        is_valid = IPCOptions.validate_ipcoptions(com_type=self.com_type, msg_type=self.msg_type, recipient=self.recipient)
        if not is_valid:
            raise ValueError(f"Invalid IPCOptions: {self.com_type}, {self.msg_type}, and {self.recipient} are compatible with one another.")
    @staticmethod
    def validate_ipcoptions(com_type: ComTypes,
                            msg_type: MsgType,
                            recipient: Recievers) -> bool:

        match recipient:
            case Recievers.REQUEST_MANAGER:
                return (com_type == ComTypes.FILESYS and IPCOptions.validate_com_msg_type_compatibility(msg_type=msg_type, com_type=com_type))
            case _:
                ...

    @staticmethod
    def validate_com_msg_type_compatibility(msg_type: MsgType, com_type: ComTypes):
        match com_type:
            case ComTypes.FILESYS:
                return msg_type == MsgType.JSON
            case _:
                ...

    @staticmethod
    def _assert_types(com_type, msg_type, recipient):
        if not isinstance(com_type, ComTypes):
            raise TypeError(f"Unrecognized ComType: {com_type}")
        if not isinstance(msg_type, MsgType):
            raise TypeError(f"Unrecognized MsgType: {msg_type}")
        if not isinstance(recipient, Recievers):
            raise TypeError(f"Unrecognized recipient: {recipient}")
