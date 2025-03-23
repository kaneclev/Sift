import logging
import threading
import time

from typing import Any, Dict, List

from api.parsing_api.ipc_management.broker import HOST, PASS, PORT, USER, MessageBroker
from api.parsing_api.ipc_management.ipc_options import Recievers
from api.parsing_api.worker import RepresentationType, Worker

logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self, rabbitmq_host=HOST, rabbitmq_port=PORT,
                 rabbitmq_user=USER, rabbitmq_pass=PASS):
        self.broker = MessageBroker(
            host=rabbitmq_host,
            port=rabbitmq_port,
            username=rabbitmq_user,
            password=rabbitmq_pass
        )

        # Define queue names
        self.script_queue = 'sift_script_queue'
        self.request_queue = 'request_manager_queue'
        self.other_service_queue = 'other_service_queue'  # Queue for other services
        self.error_queue = 'parser_error_queue'

        # Setup queues
        self._setup_queues()

        # Flag to control consumption thread
        self.should_run = True
        self.consumer_thread = None

    def _setup_queues(self):
        """Declare all necessary queues."""
        # Regular queues
        self.broker.declare_queue(self.script_queue)
        self.broker.declare_queue(self.request_queue)
        self.broker.declare_queue(self.other_service_queue)

        # Error queue
        self.broker.declare_queue(self.error_queue)

    def start_consuming(self):
        """Start consuming messages in a separate thread."""
        if self.consumer_thread is None or not self.consumer_thread.is_alive():
            self.should_run = True
            self.consumer_thread = threading.Thread(target=self._consume_scripts)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            logger.info("Started consuming messages from queue")

    def stop_consuming(self):
        """Stop consuming messages."""
        self.should_run = False
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5.0)
            logger.info("Stopped consuming messages from queue")

    def _consume_scripts(self):
        """Consume scripts from the input queue."""
        try:
            self.broker.consume(
                queue_name=self.script_queue,
                callback=self._process_script,
                auto_ack=False
            )
        except Exception as e:
            logger.error(f"Error in consumer thread: {e}")
            if self.should_run:
                logger.info("Attempting to restart consumer in 5 seconds...")
                time.sleep(5)
                self._consume_scripts()

    def _process_script(self, message: Dict[str, Any], correlation_id: str, delivery_tag: int, channel):
        """Process a script message from the queue."""
        try:
            script_content = message.get('script_content', False)
            # Check falsehood -> if false, the key does not exist, which is different from the key existing, but the script not having content
            # Message(ScriptObject) will handle the case where the script has no content
            if script_content is False:
                raise ValueError("Message must contain 'script_content'")
            message["correlation_id"] = correlation_id
            results = self.coordinate_parsing(message=message)

            # Route the results to appropriate services
            self._route_results(results, correlation_id)

            # Acknowledge the message
            self.broker.acknowledge(channel, delivery_tag)

        except Exception as e:
            logger.error(f"Error processing script: {e}")

            # Publish error message
            error_message = {
                'error': str(e),
                'original_message': message,
                'correlation_id': correlation_id
            }
            self.broker.publish(self.error_queue, error_message, correlation_id)

            # Reject the message (don't requeue if it's a validation error)
            requeue = not isinstance(e, ValueError)
            self.broker.reject(channel, delivery_tag, requeue=requeue)


    def _route_results(self, results: List[Dict[str, Any]], correlation_id: str):
        """Route parsed results to appropriate service queues."""
        for result in results:
            # Determine the target service based on the result
            recipient = result.get('recipient')

            if recipient == Recievers.REQUEST_MANAGER:
                self.broker.publish(self.request_queue, result, correlation_id)
            else:
                # Default to the other service queue for any other recipients
                self.broker.publish(self.other_service_queue, result, correlation_id)

    @staticmethod
    def coordinate_parsing(message: Dict):
        """Parse a list of scripts using workers."""
        msgs = []
        if isinstance(message, str):
            # For optional file input
            msgs.extend(Worker.parse(script=message, rtype=RepresentationType.FILE))
        else:
            msgs.extend(Worker.parse(script=message))
        return msgs

