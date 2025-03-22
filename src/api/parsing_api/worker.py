from typing import Union

from api.ipc_management.ipc_options import ComTypes, IPCOptions, MsgType, Recievers
from api.parsing_api.script_processor import ScriptProcessor
from file_operations.script_representations import (
    RepresentationType,
    ScriptObject,
    get_script_object,
)


class Worker:
    IPCOpts = IPCOptions(com_type=ComTypes.QUEUE, msg_type=MsgType.AMPQ, recipient=Recievers.REQUEST_MANAGER)
    @staticmethod
    def parse(script):
        script: Union[ScriptObject, None] = get_script_object(script, rtype=RepresentationType.FILE)
        if not script:
            return None
        proc = ScriptProcessor(script)
        ast, ir = proc.parse()
        messages = proc.send_ir(ir, options=Worker.IPCOpts)
        return messages

