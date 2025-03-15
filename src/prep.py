import os
import sys

from pathlib import Path

from dotenv import load_dotenv


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
