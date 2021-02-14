import ipaddress
from ipset import ComparisionResult, comparision_error_messages


def test_ipdeny_missing() -> None:
    comparision = ComparisionResult(
        common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
        ipdeny_missing=[ipaddress.IPv4Network("2.2.2.0/24")],
        ripestat_missing=[],
        differences_count=1,
    )
    error_messages = tuple(comparision_error_messages(comparision))
    assert len(error_messages) == 2
    assert "total number of differences: 1" in error_messages
    assert "networks present in RIPEstat but not in IPdeny: 2.2.2.0/24" in error_messages


def test_ripestat_missing() -> None:
    comparision = ComparisionResult(
        common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
        ipdeny_missing=[],
        ripestat_missing=[ipaddress.IPv4Network("3.3.3.0/24")],
        differences_count=1,
    )
    error_messages = tuple(comparision_error_messages(comparision))
    assert len(error_messages) == 2
    assert "total number of differences: 1" in error_messages
    assert "networks present in IPdeny but not in RIPEstat: 3.3.3.0/24" in error_messages


def test_both_missing() -> None:
    comparision = ComparisionResult(
        common_networks=[ipaddress.IPv4Network("1.1.1.0/24")],
        ipdeny_missing=[ipaddress.IPv4Network("2.2.2.0/24")],
        ripestat_missing=[ipaddress.IPv4Network("3.3.3.0/24")],
        differences_count=2,
    )
    error_messages = tuple(comparision_error_messages(comparision))
    assert len(error_messages) == 3
    assert "networks present in RIPEstat but not in IPdeny: 2.2.2.0/24" in error_messages
    assert "networks present in IPdeny but not in RIPEstat: 3.3.3.0/24" in error_messages
    assert "total number of differences: 2" in error_messages
