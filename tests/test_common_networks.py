import ipaddress
import pytest
from ipset import common_networks


def test_common() -> None:
    result = common_networks(
        [ipaddress.IPv4Network("1.0.0.0/24")],
        [ipaddress.IPv4Network("1.0.0.0/24")],
        0,
    )
    expected = [ipaddress.IPv4Network("1.0.0.0/24")]
    assert list(result) == expected


def test_common_with_ignored_diff() -> None:
    result = common_networks(
        [
            ipaddress.IPv4Network("1.0.0.0/24"),
            ipaddress.IPv4Network("2.0.0.0/24"),
        ],
        [ipaddress.IPv4Network("1.0.0.0/24")],
        1,
    )
    expected = [ipaddress.IPv4Network("1.0.0.0/24")]
    assert list(result) == expected


def test_exception_on_diff_limit_exceeded() -> None:
    with pytest.raises(ValueError):
        common_networks(
            [
                ipaddress.IPv4Network("1.0.0.0/24"),
                ipaddress.IPv4Network("2.0.0.0/24"),
            ],
            [ipaddress.IPv4Network("1.0.0.0/24")],
            0,
        )
