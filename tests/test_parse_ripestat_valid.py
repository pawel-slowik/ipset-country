import ipaddress
from ipset import parse_ripestat_v4, parse_ripestat_v6
from .util import read_test_file


def test_valid_v4() -> None:
    json_input = read_test_file("ripestat/valid.json")
    assert list(parse_ripestat_v4(json_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]


def test_valid_v6() -> None:
    json_input = read_test_file("ripestat/valid.json")
    assert list(parse_ripestat_v6(json_input)) == [ipaddress.IPv6Network("3fff::/20")]
