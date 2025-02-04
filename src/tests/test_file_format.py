from pathlib import Path

import pytest

from hypothesis import given, strategies as st

from file_operations.exceptions.external.file_exceptions import (
    BadExtensionError,
    NotAFileError,
    SiftFileDoesNotExistError,
)
from file_operations.sift_file import SiftFile
from prep import prep

prep()
class TestSiftFileFormats:
    def test_bad_extension(self):
        try:
            with pytest.raises(BadExtensionError):
                SiftFile(Path("tests/testsamples/file_format_errors/bad_extension.txt"))
            return  # Test passed, exit early
        except AssertionError:
            pytest.fail("Expected BadExtensionError but it was not raised.")

    def test_file_does_not_exist(self):
        try:
            with pytest.raises(SiftFileDoesNotExistError):
                SiftFile(Path("testsamples/file_format_errors/does_not_exist.sift"))
            return  # Test passed, exit early
        except AssertionError:
            pytest.fail("Expected SiftFileDoesNotExistError but it was not raised.")

    def test_not_a_file_error(self):
        try:
            with pytest.raises(NotAFileError):
                SiftFile(Path("tests/testsamples"))
            return  # Test passed, exit early
        except AssertionError:
            pytest.fail("Expected SiftFileDoesNotExistError but it was not raised.")

    @given(st.text())  # Generate random text as file paths
    def test_siftfile_fuzz_paths(self, random_path):
        try:
            file_path = Path(random_path)
            SiftFile(file_path)  # May raise exceptions

        except (SiftFileDoesNotExistError, NotAFileError, BadExtensionError):
            pass  # These are expected exceptions for invalid paths

        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")  # Report unexpected crashes