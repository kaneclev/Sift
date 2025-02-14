import os
import sys

from pathlib import Path

from dotenv import load_dotenv


def prep():
    PACKAGE_ROOT = Path(__file__).resolve().parent  # noqa: N806
    os.chdir(PACKAGE_ROOT)  # Change working directory to src/
    sys.path.insert(0, str(PACKAGE_ROOT))  # Ensure imports work
    load_dotenv(".env")
    print(f"📂 Working directory set to: {os.getcwd()}")
prep()