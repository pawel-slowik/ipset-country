import ipaddress
from typing import List
import pytest
from ipset import range_to_networks


@pytest.mark.parametrize(
    "input_range",
    (
        pytest.param("", id="empty"),
        pytest.param("foo", id="invalid format"),
        pytest.param("127.0.0.1", id="not a range"),
        pytest.param("127.0.0.1-127.0.0.256", id="invalid address in range"),
    )
)
def test_invalid(input_range: str) -> None:
    with pytest.raises(ValueError):
        range_to_networks(input_range)


@pytest.mark.parametrize(
    "input_range,expected_networks",
    (
        pytest.param(
            "192.168.10.1-192.168.10.1",
            [ipaddress.IPv4Network("192.168.10.1/32")],
            id="single address as range"
        ),
        pytest.param(
            "127.0.0.0-127.0.0.255",
            [ipaddress.IPv4Network("127.0.0.0/24")],
            id="single C class"
        ),
        pytest.param(
            "192.168.10.0-192.168.11.255",
            [ipaddress.IPv4Network("192.168.10.0/23")],
            id="two C classes"
        ),
        pytest.param(
            "192.168.10.0-192.168.12.255",
            [ipaddress.IPv4Network("192.168.10.0/23"), ipaddress.IPv4Network("192.168.12.0/24")],
            id="three C classes"
        ),
    )
)
def test_networks(input_range: str, expected_networks: List[ipaddress.IPv4Network]) -> None:
    assert list(range_to_networks(input_range)) == expected_networks
