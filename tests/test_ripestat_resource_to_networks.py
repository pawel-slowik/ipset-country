import ipaddress
import pytest
from ipset import ripestat_resource_to_networks


def test_invalid_empty() -> None:
    with pytest.raises(ipaddress.AddressValueError):
        ripestat_resource_to_networks("")


def test_invalid_format() -> None:
    with pytest.raises(ipaddress.AddressValueError):
        ripestat_resource_to_networks("foo")


def test_invalid_single_address() -> None:
    with pytest.raises(ipaddress.AddressValueError):
        ripestat_resource_to_networks("127.0.0.256")


def test_invalid_address_in_range() -> None:
    with pytest.raises(ipaddress.AddressValueError):
        ripestat_resource_to_networks("127.0.0.1-127.0.0.256")


def test_single_address() -> None:
    test = list(ripestat_resource_to_networks("127.0.0.1"))
    expected = [ipaddress.IPv4Network("127.0.0.1/32")]
    assert test == expected


def test_single_address_as_range() -> None:
    test = list(ripestat_resource_to_networks("192.168.10.1-192.168.10.1"))
    expected = [ipaddress.IPv4Network("192.168.10.1/32")]
    assert test == expected


def test_class_c() -> None:
    test = list(ripestat_resource_to_networks("127.0.0.0-127.0.0.255"))
    expected = [ipaddress.IPv4Network("127.0.0.0/24")]
    assert test == expected


def test_two_c_classes() -> None:
    test = list(ripestat_resource_to_networks("192.168.10.0-192.168.11.255"))
    expected = [ipaddress.IPv4Network("192.168.10.0/23")]
    assert test == expected


def test_three_c_classes() -> None:
    test = list(ripestat_resource_to_networks("192.168.10.0-192.168.12.255"))
    expected = [ipaddress.IPv4Network("192.168.10.0/23"), ipaddress.IPv4Network("192.168.12.0/24")]
    assert test == expected
