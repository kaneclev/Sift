from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from language.IR.ir_base import IntermediateRepresentation
from language.IR.ir_translator import RequestServiceFormats, RequestServiceFormatter


class Recipients(Enum):
    REQUEST_MANAGER = "request_manager_queue"
class Formats(Enum):
    AMPQ = "ampq"
@dataclass
class IPCOptions:
    recipient: Recipients
    format_: Formats
    correlation_id: str

class IPC:
    @staticmethod
    def create(ir_obj: IntermediateRepresentation, translations: List[IPCOptions]) -> List[Dict[str, bytes]]:
        to_send = []
        for opt in translations:
            translated_obj_to_send = IPC._form_ipc_object(ir_obj=ir_obj, recipient=opt.recipient)
            message = IPC.format_message(message=translated_obj_to_send, recipient=opt.recipient, id=opt.correlation_id)
            to_send.append(message)
        return to_send

    @staticmethod
    def _form_ipc_object(ir_obj: IntermediateRepresentation, recipient: Recipients) -> Dict:
        match recipient:
            case Recipients.REQUEST_MANAGER:
                rsf = RequestServiceFormatter(ir=ir_obj)
                request_message_as_dict = rsf.translate(format=RequestServiceFormats.JSON)
                return request_message_as_dict


    @staticmethod
    def format_message(message, recipient: Recipients, id: str):
        match recipient:
            case Recipients.REQUEST_MANAGER:
                message['id'] = id
                formatted_msg = {"recipient": recipient.value, "message": message}
                return formatted_msg
            case _:
                pass

