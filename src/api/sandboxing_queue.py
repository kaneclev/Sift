import json
import logging
import os
import sys

from api.parsing_api.ipc_management.broker import MessageBroker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def publish_script(script_content: str):
    """Publish a test script message to the 'sift_script_queue'."""
    try:
        # Instantiate the MessageBroker (credentials and connection params are loaded from environment variables)
        broker = MessageBroker()

        # Define the queue name (this should match what your parser service expects)
        queue_name = 'sift_script_queue'

        # Construct the message to publish; you can add additional keys as needed
        message = {
            'script_content': script_content,
            # Additional fields can be included here
        }

        # Publish the message; this method will return the correlation_id used
        correlation_id = broker.publish(queue_name, message)
        logger.info("Published script to queue '%s' with correlation_id: %s", queue_name, correlation_id)
    except Exception as e:
        logger.error("Failed to publish script: %s", e)
        sys.exit(1)
def read_file(fname: str) -> str:
    content = None
    print(os.getcwd())
    with open(fname, 'r') as file:
        content = file.read()
    return content
if __name__ == "__main__":
    # For testing, we use a static script content.
    # You could also extend this script to accept command line arguments if needed.
    sname = "siftscripts/ebay_use_case.sift"
    test_script = read_file(sname)
    if test_script is None or len(test_script) < 1:
        print(f"Couldnt read content from file {sname}")
    else:
        publish_script(test_script)
