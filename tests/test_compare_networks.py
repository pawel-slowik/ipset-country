import ipaddress
from typing import List
import pytest
from ipset import compare_networks, Network, ComparisionResult


@pytest.mark.parametrize(
    "ipdeny_networks,ripestat_networks,expected_result",
    (
        pytest.param(
            [ipaddress.IPv4Network("1.1.1.0/24")],
            [ipaddress.IPv4Network("1.1.1.0/24")],
            ComparisionResult(
                common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
                ipdeny_missing=[],
                ripestat_missing=[],
                differences_count=0,
            ),
            id="identical",
        ),
        pytest.param(
            [ipaddress.IPv4Network("1.1.1.0/24")],
            [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("2.2.2.0/24")],
            ComparisionResult(
                common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
                ipdeny_missing=[ipaddress.IPv4Network("2.2.2.0/24")],
                ripestat_missing=[],
                differences_count=1,
            ),
            id="IPdeny missing",
        ),
        pytest.param(
            [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("3.3.3.0/24")],
            [ipaddress.IPv4Network("1.1.1.0/24")],
            ComparisionResult(
                common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
                ipdeny_missing=[],
                ripestat_missing=[ipaddress.IPv4Network("3.3.3.0/24")],
                differences_count=1,
            ),
            id="RIPEstat missing",
        ),
        pytest.param(
            [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("3.3.3.0/24")],
            [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("2.2.2.0/24")],
            ComparisionResult(
                common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
                ipdeny_missing=[ipaddress.IPv4Network("2.2.2.0/24")],
                ripestat_missing=[ipaddress.IPv4Network("3.3.3.0/24")],
                differences_count=2,
            ),
            id="both missing",
        ),
        pytest.param(
            [ipaddress.IPv4Network("3.3.3.0/24")],
            [ipaddress.IPv4Network("2.2.2.0/24")],
            ComparisionResult(
                common_networks=[],
                ipdeny_missing=[ipaddress.IPv4Network("2.2.2.0/24")],
                ripestat_missing=[ipaddress.IPv4Network("3.3.3.0/24")],
                differences_count=2,
            ),
            id="disjoint",
        ),
    )
)
def test_comparision(
        ipdeny_networks: List[Network],
        ripestat_networks: List[Network],
        expected_result: ComparisionResult,
) -> None:
    comparision = compare_networks(ipdeny_networks, ripestat_networks)

    assert list(comparision.common_networks) == expected_result.common_networks
    assert list(comparision.ipdeny_missing) == expected_result.ipdeny_missing
    assert list(comparision.ripestat_missing) == expected_result.ripestat_missing
    assert comparision.differences_count == expected_result.differences_count
