import ipaddress
import time
from typing import List
import pytest
from pytest_mock.plugin import MockerFixture
from ipset import ipset_commands


@pytest.mark.parametrize(
    "networks,expected_commands",
    (
        pytest.param(
            [
                ipaddress.IPv4Network("127.0.0.0/24"),
            ],
            [
                "create -exist country-ZZ hash:net",
                "create country-ZZ.tmp-290619060010 hash:net",
                "add country-ZZ.tmp-290619060010 127.0.0.0/24",
                "swap country-ZZ country-ZZ.tmp-290619060010",
                "destroy country-ZZ.tmp-290619060010",
            ],
            id="single network",
        ),
        pytest.param(
            [
                ipaddress.IPv4Network("2.0.0.0/24"),
                ipaddress.IPv4Network("1.0.0.0/24"),
            ],
            [
                "create -exist country-ZZ hash:net",
                "create country-ZZ.tmp-290619060010 hash:net",
                "add country-ZZ.tmp-290619060010 1.0.0.0/24",
                "add country-ZZ.tmp-290619060010 2.0.0.0/24",
                "swap country-ZZ country-ZZ.tmp-290619060010",
                "destroy country-ZZ.tmp-290619060010",
            ],
            id="networks should be sorted",
        ),
    ),
)
def test_output(
        networks: List[ipaddress.IPv4Network],
        expected_commands: List[str],
        mocker: MockerFixture,
) -> None:
    mocker.patch("time.gmtime", return_value=time.gmtime(1876543210))

    output = list(ipset_commands("ZZ", networks))

    assert output == expected_commands
