import ipaddress
import pytest
from ipset import parse_ipdeny_v4, parse_ipdeny_v6
from .util import read_test_file


def test_valid_v4() -> None:
    text_input = read_test_file("ipdeny/valid_v4.zone")
    assert list(parse_ipdeny_v4(text_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]


def test_valid_v6() -> None:
    text_input = read_test_file("ipdeny/valid_v6.zone")
    assert list(parse_ipdeny_v6(text_input)) == [
        ipaddress.IPv6Network("3fff:0000:0000:0000:0000:0000:0000:0000/20"),
    ]


def test_error() -> None:
    text_input = read_test_file("ipdeny/invalid_v4.zone")
    with pytest.raises(ValueError):
        list(parse_ipdeny_v4(text_input))
