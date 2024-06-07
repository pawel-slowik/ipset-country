import os.path


def data_filename(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", filename)


def read_test_file(filename: str) -> bytes:
    return open(data_filename(filename), "rb").read()
