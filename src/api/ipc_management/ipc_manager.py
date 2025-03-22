import os

from typing import List

from api.ipc_management.ipc_options import IPCOptions, MsgType, Recievers
from IR.ir_base import IntermediateRepresentation
from IR.ir_translator import RequestServiceFormats, RequestServiceFormatter
from shared.utils.file_conversions import FileConverter, FileOpts, remove_suffix


class IPC:
    @staticmethod
    def send(ir_obj: IntermediateRepresentation,
             options: List[IPCOptions]):
        sent = []
        for opt in options:
            translated_obj_to_send = IPC._form_ipc_object(ir_obj=ir_obj, recipient=opt.recipient, form=opt.msg_type)
            sent_confirmation = IPC.handle_message(message=translated_obj_to_send,
                               recipient=opt.recipient,
                               form=opt.msg_type,
                               identifier=ir_obj.identifier)
            sent.append({opt.msg_type: sent_confirmation})
        return sent

    @staticmethod
    def _form_ipc_object(ir_obj: IntermediateRepresentation, recipient: Recievers, form: MsgType):
        match form:
            case MsgType.JSON:
                return IPC._json_ir_translation(ir_obj=ir_obj, recipient=recipient)
            case _:
                pass

    @staticmethod
    def _json_ir_translation(ir_obj: IntermediateRepresentation, recipient: Recievers):
        match recipient:
            case Recievers.REQUEST_MANAGER:
                rsf = RequestServiceFormatter(ir=ir_obj)
                return rsf.translate(format=RequestServiceFormats.JSON)
            case _:
                pass

    @staticmethod
    def handle_message(message, recipient: Recievers, form: MsgType, identifier: str = ""):
        match form:
            case MsgType.JSON:
                assert identifier.strip() != ""
                filename = IPC._assign_correct_filename(filename=identifier, recipient=recipient)
                return IPC._send_file_msg(message=message, ftype=FileOpts.JSON, filename=filename, recipient=recipient)
            case _:
                pass

    @staticmethod
    def _assign_correct_filename(filename: str, recipient: Recievers):
        match recipient:
            case Recievers.REQUEST_MANAGER:
                no_extension = remove_suffix(file_name=filename)
                no_extension = no_extension + "-reqmsg-url-alias"
                return no_extension
            case _:
                pass

    @staticmethod
    def _send_file_msg(message, ftype: FileOpts, filename: str, recipient: Recievers):
        match recipient:
            case Recievers.REQUEST_MANAGER:
                if (request_com_base_dir := os.environ.get("REQUEST_COM", None)) is None:
                    raise ValueError("Expected environment variable 'REQUEST_COM' to be registered; is it there? Did we load the environment?")
                save_dir = os.path.join(request_com_base_dir, "Sent")
                saved_to_file = FileConverter.save_as(save_to_dir=save_dir,
                                       raw_basename=os.path.basename(filename),
                                       ftype=ftype, object_to_save=message)
                return saved_to_file
            case _:
                ...
