import pytest
from ipset import parse_ripestat
from .util import read_test_file


def test_explain_error_on_status_code() -> None:
    json_input = read_test_file("ripestat/error_status_code.json")
    with pytest.raises(ValueError, match="status_code=201"):
        parse_ripestat(json_input)


def test_explain_error_on_status() -> None:
    json_input = read_test_file("ripestat/error_status.json")
    with pytest.raises(ValueError, match="status=not ok"):
        parse_ripestat(json_input)


def test_explain_error_on_data_call_status() -> None:
    json_input = read_test_file("ripestat/error_data_call_status.json")
    with pytest.raises(ValueError, match="data_call_status.*deprecated"):
        parse_ripestat(json_input)


def test_message_on_error() -> None:
    json_input = read_test_file("ripestat/error_message.json")
    with pytest.raises(ValueError, match="message=foo bar"):
        parse_ripestat(json_input)


def test_messages_on_error() -> None:
    json_input = read_test_file("ripestat/error_messages.json")
    with pytest.raises(ValueError, match="(?s)message=foo.*bar"):
        parse_ripestat(json_input)
