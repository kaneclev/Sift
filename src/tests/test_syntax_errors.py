from pathlib import Path

import pytest

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
)
from file_operations.sift_file import SiftFile
from prep import prep

prep()
