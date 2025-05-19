import pytest
from ipset import parse_ripestat_v4
from .util import read_test_file


def test_error_on_status_code() -> None:
    json_input = read_test_file("ripestat/error_status_code.json")
    with pytest.raises(ValueError):
        parse_ripestat_v4(json_input)


def test_error_on_status() -> None:
    json_input = read_test_file("ripestat/error_status.json")
    with pytest.raises(ValueError):
        parse_ripestat_v4(json_input)


def test_error_on_data_call_status() -> None:
    json_input = read_test_file("ripestat/error_data_call_status.json")
    with pytest.raises(ValueError):
        parse_ripestat_v4(json_input)


def test_error_on_invalid_data() -> None:
    json_input = read_test_file("ripestat/error_in_list.json")
    with pytest.raises(ValueError):
        list(parse_ripestat_v4(json_input))
