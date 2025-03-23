from typing import Union, List, Dict, Any

from api.parsing_api.ipc_management.ipc_options import ComTypes, IPCOptions, MsgType, Recievers
from api.parsing_api.script_processor import ScriptProcessor
from file_operations.script_representations import (
    RepresentationType,
    ScriptObject,
    get_script_object,
)

class Worker:
    """Worker class that handles parsing individual scripts."""
    
    @staticmethod
    def parse(script, rtype: RepresentationType = RepresentationType.MESSAGE) -> List[Dict[str, Any]]:
        """
        Parse a script file and prepare messages for the appropriate recipients.
        
        Args:
            script: Path to the script or a ScriptObject
            
        Returns:
            List of message dictionaries ready to be sent to various services
        """
        # Get the script object from file
        script_obj: Union[ScriptObject, None] = get_script_object(script, rtype=rtype)
        if not script_obj:
            return []
        
        return Worker._process_script_object(script_obj)
    
    
    @staticmethod
    def _process_script_object(script_obj: ScriptObject) -> List[Dict[str, Any]]:
        """
        Process a script object and generate messages for different services.
        
        Args:
            script_obj: The ScriptObject to process
            
        Returns:
            List of message dictionaries ready to be sent to various services
        """
        # Process the script
        proc = ScriptProcessor(script_obj)
        ast, ir = proc.parse()
        
        # Prepare messages for different services
        messages = []
        
        # Create options for the Request Manager
        #! TODO: Remember; the IPC iterates over the ICPOptions, not the IR. In other words, for each set of IPCOptions defined, it will transform the IR in a different ways
        #   Therefore, the next step for communicating with other services besides the RequestManager will be to define ways of transforming the IR into a format that
        #   something like the 'Extractor' service will understand.
        request_manager_opts = IPCOptions(
            com_type=ComTypes.QUEUE,
            msg_type=MsgType.AMPQ,
            recipient=Recievers.REQUEST_MANAGER
        )
        
        # Get messages for the Request Manager
        request_messages = proc.make_ir(ir, options=request_manager_opts)
        # NOTE: The make_ir method already inserts a 'recipient' key.
        messages.extend(request_messages)
        
        return messages