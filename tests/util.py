import os.path
from typing import IO


def data_filename(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", filename)


def open_test_file(filename: str) -> IO[bytes]:
    return open(data_filename(filename), "rb")
