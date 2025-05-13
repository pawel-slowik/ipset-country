import ipaddress
import time
from pytest_mock.plugin import MockerFixture
from ipset import ipset_commands


def test_output(mocker: MockerFixture) -> None:
    mocker.patch("time.gmtime", return_value=time.gmtime(1876543210))
    expected = [
        "create -exist country-ZZ hash:net",
        "create country-ZZ.tmp-20290619060010 hash:net",
        "add country-ZZ.tmp-20290619060010 127.0.0.0/24",
        "swap country-ZZ country-ZZ.tmp-20290619060010",
        "destroy country-ZZ.tmp-20290619060010",
    ]

    output = list(ipset_commands("ZZ", [ipaddress.IPv4Network("127.0.0.0/24")]))

    assert output == expected


def test_order() -> None:
    output = list(ipset_commands(
        "ZZ",
        [
            ipaddress.IPv4Network("2.0.0.0/24"),
            ipaddress.IPv4Network("1.0.0.0/24"),
        ],
    ))

    assert output[2].endswith(" 1.0.0.0/24")
    assert output[3].endswith(" 2.0.0.0/24")
