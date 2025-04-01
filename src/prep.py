import os
import sys

from pathlib import Path

from dotenv import load_dotenv

from language.exceptions.external_exception import SyntaxError


def custom_excepthook(exctype, value, tb):
    if isinstance(value, SyntaxError):
        print(value)  # Only print your custom error message.
    else:
        # For other exceptions, use the default behavior.
        sys.__excepthook__(exctype, value, tb)
sys.excepthook = custom_excepthook

def prep():
    """ Prepares the environment for the execution of the Sift module.

    Defines the root of the package so that all files can share the same cwd,
    for consistent pathing purposes.

    *Auto-called on import.*
    """
    PACKAGE_ROOT = Path(__file__).resolve().parent  # noqa: N806
    os.chdir(os.path.dirname(PACKAGE_ROOT))  # Change working directory to src/
    sys.path.insert(0, str(PACKAGE_ROOT))  # Ensure imports work
    print(f"📂 Working directory set to: {os.getcwd()}")
    loaded = load_dotenv(".env")
    if loaded:
        print("Loaded environment. ")
    else:
        raise FileNotFoundError("Could not find the .env file in the CWD...")
prep()
