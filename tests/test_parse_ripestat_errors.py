import pytest
from ipset import parse_ripestat
from .util import open_test_file


def test_error_on_status_code() -> None:
    with open_test_file("ripestat/error_status_code.json") as json_input:
        with pytest.raises(ValueError):
            parse_ripestat(json_input)


def test_error_on_status() -> None:
    with open_test_file("ripestat/error_status.json") as json_input:
        with pytest.raises(ValueError):
            parse_ripestat(json_input)


def test_error_on_data_call_status() -> None:
    with open_test_file("ripestat/error_data_call_status.json") as json_input:
        with pytest.raises(ValueError):
            parse_ripestat(json_input)


def test_error_on_invalid_data() -> None:
    with open_test_file("ripestat/error_in_list.json") as json_input:
        with pytest.raises(ValueError):
            list(parse_ripestat(json_input))
