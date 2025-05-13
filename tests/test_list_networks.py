import ipaddress
import pytest
from pytest_mock.plugin import MockerFixture
from ipset import list_networks


def test_common(mocker: MockerFixture) -> None:
    mocker.patch("ipset.list_ipdeny", return_value=[ipaddress.IPv4Network("1.0.0.0/24")])
    mocker.patch("ipset.list_ripestat", return_value=[ipaddress.IPv4Network("1.0.0.0/24")])

    result = list_networks("ZZ", 0)

    assert list(result) == [ipaddress.IPv4Network("1.0.0.0/24")]


def test_common_with_ignored_diff(mocker: MockerFixture) -> None:
    mocker.patch(
        "ipset.list_ipdeny",
        return_value=[
            ipaddress.IPv4Network("1.0.0.0/24"),
            ipaddress.IPv4Network("2.0.0.0/24"),
        ],
    )
    mocker.patch(
        "ipset.list_ripestat",
        return_value=[
            ipaddress.IPv4Network("1.0.0.0/24"),
        ],
    )

    result = list_networks("ZZ", 1)

    assert list(result) == [ipaddress.IPv4Network("1.0.0.0/24")]


def test_exception_on_diff_limit_exceeded(mocker: MockerFixture) -> None:
    mocker.patch(
        "ipset.list_ipdeny",
        return_value=[
            ipaddress.IPv4Network("1.0.0.0/24"),
            ipaddress.IPv4Network("2.0.0.0/24"),
        ],
    )
    mocker.patch(
        "ipset.list_ripestat",
        return_value=[
            ipaddress.IPv4Network("1.0.0.0/24"),
        ],
    )

    with pytest.raises(ValueError):
        list_networks("ZZ", 0)
