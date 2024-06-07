import ipaddress
from ipset import parse_ripestat
from .util import read_test_file


def test_valid() -> None:
    json_input = read_test_file("ripestat/valid.json")
    assert list(parse_ripestat(json_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]
