import ipaddress
import pytest
from ipset import parse_ipdeny
from .util import open_test_file


def test_valid() -> None:
    with open_test_file("ipdeny/valid.zone") as text_input:
        assert list(parse_ipdeny(text_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]


def test_error() -> None:
    with open_test_file("ipdeny/invalid.zone") as text_input:
        with pytest.raises(ValueError):
            list(parse_ipdeny(text_input))
