import argparse  # noqa: I001
import logging
import signal
import sys
import os
import threading

from prep import prep  # noqa: F401
from api.language_api.coordinator import Coordinator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OPTS = {}
coordinator = None

# Create a threading event to block the main thread on Windows
stop_event = threading.Event()

def signal_handler(sig, frame):
    """Handle process termination signals."""
    stop_event.set()  # Unblocks the main thread
    sys.exit(0)

def start_queue_communication():
    """Start the queue communication mode."""
    global coordinator

    # Create a coordinator instance
    coordinator = Coordinator()

    # Start consuming messages
    coordinator.start_consuming()

    logger.info("Parser service is running in queue mode. Press CTRL+C to exit.")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Block the main thread until a shutdown signal is received
    try:
        if os.name == 'nt':  # Windows
            # Loop with a short timeout to allow responsive signal handling
            while not stop_event.is_set():
                stop_event.wait(0.1)
        else:
            # On Unix-like systems, use signal.pause()
            signal.pause()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
        coordinator.stop_consuming()

def manual_compile(fname: str):
    from api.language_api.script_processor import ScriptProcessor
    proc = ScriptProcessor(fname)
    ast, ir = proc.parse()
    print(f'Parsed to AST: {ast}, IR: {ir}')

def start_file_communication(fname: str):
    """Process a file directly (legacy mode)."""
    # Create a coordinator instance for one-off processing
    temp_coordinator = Coordinator()

    # Process the file
    generated = temp_coordinator.coordinate_parsing(fname)
    print(generated)

def arg_handler(parser: argparse.ArgumentParser) -> bool:
    """Handle command line arguments."""
    parser.add_argument("--man", help="Manually feed a file instead of using the queue.", required=False)
    parser.add_argument("--no-queue", help="Feed a file using 'man' without using a RabbitMQ process; only compile", action="store_true")
    args = parser.parse_args()
    for arg in vars(args):
        OPTS[arg] = getattr(args, arg)
    return True

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Sift Parser Service")
    valid_args = arg_handler(parser)

    if not valid_args:
        return

    if OPTS["man"] is not None:
        if OPTS["no_queue"]:
            manual_compile(fname=OPTS["man"])
        else:
            start_file_communication(OPTS["man"])
        return
    start_queue_communication()

if __name__ == "__main__":
    main()
