#!/usr/bin/env python3

import ipaddress
import itertools
import json
import urllib.parse
import urllib.request
import urllib.error
import time
import http.client
from http import HTTPStatus
from typing import Iterable, Mapping, Collection, NamedTuple, Union, Optional, Any
import argparse


Network = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]


class ComparisionResult(NamedTuple):
    common_networks: Collection[Network]
    ipdeny_missing: Collection[Network]
    ripestat_missing: Collection[Network]
    differences_count: int

    def describe(self) -> Iterable[str]:
        if self.ripestat_missing:
            yield "networks present in IPdeny but not in RIPEstat: " + ", ".join(
                map(str, self.ripestat_missing)
            )
        if self.ipdeny_missing:
            yield "networks present in RIPEstat but not in IPdeny: " + ", ".join(
                map(str, self.ipdeny_missing)
            )
        yield f"total number of differences: {self.differences_count}"


def list_ipdeny(country_code: str) -> Iterable[Network]:
    yield from parse_ipdeny_v4(read_url(get_ipdeny_v4_url(country_code)))
    try:
        v6_response = read_url(get_ipdeny_v6_url(country_code))
    except urllib.error.HTTPError as http_error:
        if http_error.code == HTTPStatus.NOT_FOUND:
            # some countries don't have any IPv6 presence
            return
        raise
    yield from parse_ipdeny_v6(v6_response)


def get_ipdeny_v4_url(country_code: str) -> str:
    return f"http://www.ipdeny.com/ipblocks/data/aggregated/{country_code}-aggregated.zone"


def parse_ipdeny_v4(text_input: bytes) -> Iterable[ipaddress.IPv4Network]:
    return (
        ipaddress.IPv4Network(input_network.decode("ascii").strip())
        for input_network in text_input.splitlines()
    )


def get_ipdeny_v6_url(country_code: str) -> str:
    return f"http://www.ipdeny.com/ipv6/ipaddresses/aggregated/{country_code}-aggregated.zone"


def parse_ipdeny_v6(text_input: bytes) -> Iterable[ipaddress.IPv6Network]:
    return (
        ipaddress.IPv6Network(input_network.decode("ascii").strip())
        for input_network in text_input.splitlines()
    )


def list_ripestat(country_code: str) -> Iterable[Network]:
    response = read_url(get_ripestat_url(country_code))
    v4_networks = parse_ripestat_v4(response)
    v6_networks = parse_ripestat_v6(response)

    # RIPEstat data is not aggregated, needs collapsing
    v4_networks = ipaddress.collapse_addresses(v4_networks)
    v6_networks = ipaddress.collapse_addresses(v6_networks)

    yield from v4_networks
    yield from v6_networks


def get_ripestat_url(country_code: str) -> str:
    return f"https://stat.ripe.net/data/country-resource-list/data.json?resource={country_code}"


def parse_ripestat_v4(json_input: bytes) -> Iterable[ipaddress.IPv4Network]:
    response = json.loads(json_input)
    check_ripestat_response(response)
    return itertools.chain.from_iterable(
        ripestat_resource_to_networks(input_network)
        for input_network in response["data"]["resources"]["ipv4"]
    )


def parse_ripestat_v6(json_input: bytes) -> Iterable[ipaddress.IPv6Network]:
    response = json.loads(json_input)
    check_ripestat_response(response)
    for input_network in response["data"]["resources"]["ipv6"]:
        yield ipaddress.IPv6Network(input_network)


def check_ripestat_response(response: Any) -> None:

    def error_message(error_response: Mapping) -> Optional[str]:
        if "message" in error_response:
            return str(response["message"])
        if "messages" in error_response:
            return "\n".join(error_response["messages"])
        return None

    if response["status_code"] != HTTPStatus.OK or response["status"] != "ok":
        raise ValueError(
            "error in RIPEstat response: " +
            f"status_code={response['status_code']}, " +
            f"status={response['status']}, " +
            f"message={error_message(response)}"
        )
    if not response["data_call_status"].startswith("supported"):
        raise ValueError(f"unexpected RIPEstat data_call_status: {response['data_call_status']}")


def ripestat_resource_to_networks(network_spec: str) -> Iterable[ipaddress.IPv4Network]:

    def range_to_networks(network_range: str) -> Iterable[ipaddress.IPv4Network]:
        parts = network_range.split("-")
        if len(parts) != 2:
            raise ValueError
        first = ipaddress.IPv4Address(parts[0])
        last = ipaddress.IPv4Address(parts[1])
        return ipaddress.summarize_address_range(first, last)

    try:
        return [ipaddress.IPv4Network(network_spec)]
    except ipaddress.AddressValueError:
        try:
            return range_to_networks(network_spec)
        except ValueError:
            pass
        raise


def read_url(url: str) -> bytes:
    response : http.client.HTTPResponse
    with urllib.request.urlopen(url) as response:
        if response.getcode() != HTTPStatus.OK:
            raise ValueError(f"unexpected HTTP code: {response.getcode()}")
        return response.read()


def list_networks(country_code: str, max_diff: int = 0) -> Iterable[Network]:
    ipdeny_networks = list_ipdeny(country_code)
    ripestat_networks = list_ripestat(country_code)
    comparision = compare_networks(ipdeny_networks, ripestat_networks)
    if comparision.differences_count > max_diff:
        raise ValueError("\n".join(comparision.describe()))
    return comparision.common_networks


def compare_networks(
        ipdeny_networks: Iterable[Network],
        ripestat_networks: Iterable[Network],
) -> ComparisionResult:
    ipdeny_networks = frozenset(ipdeny_networks)
    ripestat_networks = frozenset(ripestat_networks)
    return ComparisionResult(
        common_networks=ipdeny_networks & ripestat_networks,
        ipdeny_missing=ripestat_networks - ipdeny_networks,
        ripestat_missing=ipdeny_networks - ripestat_networks,
        differences_count=len(ipdeny_networks ^ ripestat_networks),
    )


def ipset_commands(country_code: str, networks: Iterable[Network]) -> Iterable[str]:
    version_family_map = {
        4: "inet",
        6: "inet6",
    }
    networks_grouped_by_version: dict[int, list[Network]] = {
        4: [],
        6: [],
    }
    for network in networks:
        networks_grouped_by_version[network.version].append(network)
    for version, version_networks in networks_grouped_by_version.items():
        family = version_family_map[version]
        set_name = create_target_set_name(country_code, version)
        tmp_set_name = create_temporary_set_name(country_code, version)
        header = (
            f"create -exist {set_name} hash:net family {family}",
            f"create {tmp_set_name} hash:net family {family}",
        )
        footer = (
            f"swap {set_name} {tmp_set_name}",
            f"destroy {tmp_set_name}",
        )
        commands = (
            f"add {tmp_set_name} {network}"
            for network in sorted(version_networks)
        )
        yield from itertools.chain(header, commands, footer)


def create_target_set_name(country_code: str, version: int) -> str:
    return f"country-{country_code}-v{version}"


def create_temporary_set_name(country_code: str, version: int) -> str:
    return f"country-{country_code}-v{version}.tmp-{time.strftime('%y%m%d%H%M%S', time.gmtime())}"


def ipset(country_code: str, max_diff: int = 0) -> Iterable[str]:
    return ipset_commands(country_code, list_networks(country_code, max_diff))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a country based IP set for packet filtering in the Linux kernel."
    )
    parser.add_argument("country_code", help="two letter ISO-3166 country code")
    parser.add_argument(
        "-i", dest="max_diff", type=int, metavar="N", default=0,
        help="ignore up to N networks of difference between data sources"
    )
    args = parser.parse_args()
    for line in ipset(args.country_code, args.max_diff):
        print(line)


if __name__ == "__main__":
    main()
