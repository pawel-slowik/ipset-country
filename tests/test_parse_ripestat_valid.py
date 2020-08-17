import ipaddress
from ipset import parse_ripestat
from .util import open_test_file


def test_valid() -> None:
    with open_test_file("ripestat/valid.json") as json_input:
        assert list(parse_ripestat(json_input)) == [ipaddress.IPv4Network("127.0.0.0/24")]
