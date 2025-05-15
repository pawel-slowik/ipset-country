import ipaddress
from typing import List
import pytest
from ipset import ripestat_resource_to_networks


@pytest.mark.parametrize(
    "input_resource",
    (
        pytest.param("", id="empty"),
        pytest.param("foo", id="invalid format"),
        pytest.param("127.0.0.256", id="invalid single address"),
        pytest.param("127.0.0.1-127.0.0.256", id="invalid address in range"),
    )
)
def test_invalid(input_resource: str) -> None:
    with pytest.raises(ipaddress.AddressValueError):
        ripestat_resource_to_networks(input_resource)


@pytest.mark.parametrize(
    "input_resource,expected_networks",
    (
        pytest.param(
            "127.0.0.1",
            [ipaddress.IPv4Network("127.0.0.1/32")],
            id="single address"
        ),
        pytest.param(
            "192.168.10.1-192.168.10.1",
            [ipaddress.IPv4Network("192.168.10.1/32")],
            id="single address as range"
        ),
        pytest.param(
            "127.0.0.0-127.0.0.255",
            [ipaddress.IPv4Network("127.0.0.0/24")],
            id="C class"
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
def test_networks(input_resource: str, expected_networks: List[ipaddress.IPv4Network]) -> None:
    assert list(ripestat_resource_to_networks(input_resource)) == expected_networks
