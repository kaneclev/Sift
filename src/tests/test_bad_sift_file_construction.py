from pathlib import Path

import pytest

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
)
from file_operations.sift_file import SiftFile
from prep import prep

prep()


class TestBadSiftFileConstruction:
    def test_bad_extension(self):
        try:
            with pytest.raises(BadExtensionError):
                SiftFile(Path("tests/testsamples/file_format_errors/bad_extension.txt"))
            return  # Test passed, exit early
        except AssertionError:
            pytest.fail("Expected BadExtensionError but it was not raised.")

