import pytest
from ipset import parse_ripestat
from .util import open_test_file

def test_explain_error_on_status_code() -> None:
    with open_test_file("ripestat/error_status_code.json") as json_input:
        with pytest.raises(ValueError, match="status_code=201"):
            parse_ripestat(json_input)

def test_explain_error_on_status() -> None:
    with open_test_file("ripestat/error_status.json") as json_input:
        with pytest.raises(ValueError, match="status=not ok"):
            parse_ripestat(json_input)

def test_explain_error_on_data_call_status() -> None:
    with open_test_file("ripestat/error_data_call_status.json") as json_input:
        with pytest.raises(ValueError, match="data_call_status.*deprecated"):
            parse_ripestat(json_input)

def test_message_on_error() -> None:
    with open_test_file("ripestat/error_message.json") as json_input:
        with pytest.raises(ValueError, match="message=foo bar"):
            parse_ripestat(json_input)

def test_messages_on_error() -> None:
    with open_test_file("ripestat/error_messages.json") as json_input:
        with pytest.raises(ValueError, match="(?s)message=foo.*bar"):
            parse_ripestat(json_input)
