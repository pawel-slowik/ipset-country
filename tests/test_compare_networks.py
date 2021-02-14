import ipaddress
from ipset import compare_networks


def test_identical() -> None:
    comparision = compare_networks(
        [ipaddress.IPv4Network("1.1.1.0/24")],
        [ipaddress.IPv4Network("1.1.1.0/24")],
    )
    assert list(comparision.common_networks) == [ipaddress.IPv4Network("1.1.1.0/24")]
    assert not comparision.ipdeny_missing
    assert not comparision.ripestat_missing
    assert comparision.differences_count == 0


def test_ipdeny_missing() -> None:
    comparision = compare_networks(
        [ipaddress.IPv4Network("1.1.1.0/24")],
        [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("2.2.2.0/24")],
    )
    assert list(comparision.common_networks) == [ipaddress.IPv4Network("1.1.1.0/24")]
    assert list(comparision.ipdeny_missing) == [ipaddress.IPv4Network("2.2.2.0/24")]
    assert not comparision.ripestat_missing
    assert comparision.differences_count == 1


def test_ripestat_missing() -> None:
    comparision = compare_networks(
        [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("3.3.3.0/24")],
        [ipaddress.IPv4Network("1.1.1.0/24")],
    )
    assert list(comparision.common_networks) == [ipaddress.IPv4Network("1.1.1.0/24")]
    assert not comparision.ipdeny_missing
    assert list(comparision.ripestat_missing) == [ipaddress.IPv4Network("3.3.3.0/24")]
    assert comparision.differences_count == 1


def test_both_missing() -> None:
    comparision = compare_networks(
        [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("3.3.3.0/24")],
        [ipaddress.IPv4Network("1.1.1.0/24"), ipaddress.IPv4Network("2.2.2.0/24")],
    )
    assert list(comparision.common_networks) == [ipaddress.IPv4Network("1.1.1.0/24")]
    assert list(comparision.ipdeny_missing) == [ipaddress.IPv4Network("2.2.2.0/24")]
    assert list(comparision.ripestat_missing) == [ipaddress.IPv4Network("3.3.3.0/24")]
    assert comparision.differences_count == 2


def test_disjoint() -> None:
    comparision = compare_networks(
        [ipaddress.IPv4Network("3.3.3.0/24")],
        [ipaddress.IPv4Network("2.2.2.0/24")],
    )
    assert not comparision.common_networks
    assert list(comparision.ipdeny_missing) == [ipaddress.IPv4Network("2.2.2.0/24")]
    assert list(comparision.ripestat_missing) == [ipaddress.IPv4Network("3.3.3.0/24")]
    assert comparision.differences_count == 2
