import ipaddress
import pytest
from ipset import parse_ipdeny
from .util import read_test_file


def test_valid() -> None:
    text_input = read_test_file("ipdeny/valid.zone")
    assert list(parse_ipdeny(text_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]


def test_error() -> None:
    text_input = read_test_file("ipdeny/invalid.zone")
    with pytest.raises(ValueError):
        list(parse_ipdeny(text_input))
