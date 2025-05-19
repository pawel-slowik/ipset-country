import ipaddress
import time
from typing import List
import pytest
from pytest_mock.plugin import MockerFixture
from ipset import Network, ipset_commands


@pytest.mark.parametrize(
    "networks,expected_commands",
    (
        pytest.param(
            [
                ipaddress.IPv4Network("127.0.0.0/24"),
            ],
            [
                "create -exist country-ZZ-v4 hash:net family inet",
                "create country-ZZ-v4.tmp-290619060010 hash:net family inet",
                "add country-ZZ-v4.tmp-290619060010 127.0.0.0/24",
                "swap country-ZZ-v4 country-ZZ-v4.tmp-290619060010",
                "destroy country-ZZ-v4.tmp-290619060010",
                "create -exist country-ZZ-v6 hash:net family inet6",
                "create country-ZZ-v6.tmp-290619060010 hash:net family inet6",
                "swap country-ZZ-v6 country-ZZ-v6.tmp-290619060010",
                "destroy country-ZZ-v6.tmp-290619060010",
            ],
            id="single IPv4 network",
        ),
        pytest.param(
            [
                ipaddress.IPv6Network("3fff::/20"),
            ],
            [
                "create -exist country-ZZ-v4 hash:net family inet",
                "create country-ZZ-v4.tmp-290619060010 hash:net family inet",
                "swap country-ZZ-v4 country-ZZ-v4.tmp-290619060010",
                "destroy country-ZZ-v4.tmp-290619060010",
                "create -exist country-ZZ-v6 hash:net family inet6",
                "create country-ZZ-v6.tmp-290619060010 hash:net family inet6",
                "add country-ZZ-v6.tmp-290619060010 3fff::/20",
                "swap country-ZZ-v6 country-ZZ-v6.tmp-290619060010",
                "destroy country-ZZ-v6.tmp-290619060010",
            ],
            id="single IPv6 network",
        ),
        pytest.param(
            [
                ipaddress.IPv4Network("2.0.0.0/24"),
                ipaddress.IPv4Network("1.0.0.0/24"),
            ],
            [
                "create -exist country-ZZ-v4 hash:net family inet",
                "create country-ZZ-v4.tmp-290619060010 hash:net family inet",
                "add country-ZZ-v4.tmp-290619060010 1.0.0.0/24",
                "add country-ZZ-v4.tmp-290619060010 2.0.0.0/24",
                "swap country-ZZ-v4 country-ZZ-v4.tmp-290619060010",
                "destroy country-ZZ-v4.tmp-290619060010",
                "create -exist country-ZZ-v6 hash:net family inet6",
                "create country-ZZ-v6.tmp-290619060010 hash:net family inet6",
                "swap country-ZZ-v6 country-ZZ-v6.tmp-290619060010",
                "destroy country-ZZ-v6.tmp-290619060010",
            ],
            id="networks should be sorted",
        ),
    ),
)
def test_output(
        networks: List[Network],
        expected_commands: List[str],
        mocker: MockerFixture,
) -> None:
    mocker.patch("time.gmtime", return_value=time.gmtime(1876543210))

    output = list(ipset_commands("ZZ", networks))

    assert output == expected_commands
