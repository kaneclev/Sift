
from typing import Any, Dict, List, Union

from api.language_api.script_processor import ScriptProcessor
from api.language_api.script_representations import (
    RepresentationType,
    ScriptObject,
    get_script_object,
)


class Worker:
    """Worker class that handles parsing individual scripts."""

    @staticmethod
    def parse(script: Union[str, Dict], rtype: RepresentationType = RepresentationType.MESSAGE) -> List[Dict[str, Any]]:
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

        # Get messages for the Request Manager
        #request_messages = proc.make_message(ir, recipient=Recipients.REQUEST_MANAGER, correlation_id=script_obj.get_id())
        #messages.extend(request_messages)
        return messages
