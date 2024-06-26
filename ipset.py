#!/usr/bin/env python3

import ipaddress
import itertools
import json
import urllib.parse
import urllib.request
import time
import http.client
from http import HTTPStatus
from typing import Iterable, Mapping, Collection, NamedTuple, Optional
import argparse


class ComparisionResult(NamedTuple):
    common_networks: Collection[ipaddress.IPv4Network]
    ipdeny_missing: Collection[ipaddress.IPv4Network]
    ripestat_missing: Collection[ipaddress.IPv4Network]
    differences_count: int


def list_ipdeny(country_code: str) -> Iterable[ipaddress.IPv4Network]:
    return parse_ipdeny(read_url(get_ipdeny_url(country_code)))


def get_ipdeny_url(country_code: str) -> str:
    return f"http://www.ipdeny.com/ipblocks/data/aggregated/{country_code}-aggregated.zone"


def parse_ipdeny(text_input: bytes) -> Iterable[ipaddress.IPv4Network]:
    return (
        ipaddress.IPv4Network(input_network.decode("ascii").strip())
        for input_network in text_input.splitlines()
    )


def list_ripestat(country_code: str) -> Iterable[ipaddress.IPv4Network]:
    networks = parse_ripestat(read_url(get_ripestat_url(country_code)))
    # RIPEstat data is not aggregated, needs collapsing
    networks = ipaddress.collapse_addresses(networks)
    return networks


def get_ripestat_url(country_code: str) -> str:
    return f"https://stat.ripe.net/data/country-resource-list/data.json?resource={country_code}"


def parse_ripestat(json_input: bytes) -> Iterable[ipaddress.IPv4Network]:

    def error_message(error_response: Mapping) -> Optional[str]:
        if "message" in error_response:
            return str(response["message"])
        if "messages" in error_response:
            return "\n".join(error_response["messages"])
        return None

    response = json.loads(json_input)
    if response["status_code"] != HTTPStatus.OK or response["status"] != "ok":
        raise ValueError(
            "error in RIPEstat response: " +
            f"status_code={response['status_code']}, " +
            f"status={response['status']}, " +
            f"message={error_message(response)}"
        )
    if not response["data_call_status"].startswith("supported"):
        raise ValueError(f"unexpected RIPEstat data_call_status: {response['data_call_status']}")
    return itertools.chain.from_iterable(
        ripestat_resource_to_networks(input_network)
        for input_network in response["data"]["resources"]["ipv4"]
    )


def ripestat_resource_to_networks(network_spec: str) -> Iterable[ipaddress.IPv4Network]:
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


def range_to_networks(network_range: str) -> Iterable[ipaddress.IPv4Network]:
    parts = network_range.split("-")
    if len(parts) != 2:
        raise ValueError
    first = ipaddress.IPv4Address(parts[0])
    last = ipaddress.IPv4Address(parts[1])
    return ipaddress.summarize_address_range(first, last)


def list_networks(country_code: str, max_diff: int = 0) -> Iterable[ipaddress.IPv4Network]:
    return common_networks(list_ipdeny(country_code), list_ripestat(country_code), max_diff)


def common_networks(
        ipdeny_networks: Iterable[ipaddress.IPv4Network],
        ripestat_networks: Iterable[ipaddress.IPv4Network],
        max_diff: int,
    ) -> Iterable[ipaddress.IPv4Network]:
    comparision = compare_networks(ipdeny_networks, ripestat_networks)
    if comparision.differences_count > max_diff:
        raise ValueError("\n".join(comparision_error_messages(comparision)))
    return comparision.common_networks


def compare_networks(
        ipdeny_networks: Iterable[ipaddress.IPv4Network],
        ripestat_networks: Iterable[ipaddress.IPv4Network],
) -> ComparisionResult:
    ipdeny_networks = frozenset(ipdeny_networks)
    ripestat_networks = frozenset(ripestat_networks)
    return ComparisionResult(
        common_networks=ipdeny_networks & ripestat_networks,
        ipdeny_missing=ripestat_networks - ipdeny_networks,
        ripestat_missing=ipdeny_networks - ripestat_networks,
        differences_count=len(ipdeny_networks ^ ripestat_networks),
    )


def comparision_error_messages(comparision: ComparisionResult) -> Iterable[str]:
    if comparision.ripestat_missing:
        yield "networks present in IPdeny but not in RIPEstat: " + ", ".join(
            map(str, comparision.ripestat_missing)
        )
    if comparision.ipdeny_missing:
        yield "networks present in RIPEstat but not in IPdeny: " + ", ".join(
            map(str, comparision.ipdeny_missing)
        )
    yield f"total number of differences: {comparision.differences_count}"


def ipset_commands(country_code: str, networks: Iterable[ipaddress.IPv4Network]) -> Iterable[str]:
    set_name = create_target_set_name(country_code)
    tmp_set_name = create_temporary_set_name(country_code)
    header = (
        f"create -exist {set_name} hash:net",
        f"create {tmp_set_name} hash:net",
    )
    footer = (
        f"swap {set_name} {tmp_set_name}",
        f"destroy {tmp_set_name}",
    )
    commands = (
        f"add {tmp_set_name} {network}"
        for network in sorted(networks)
    )
    return itertools.chain(header, commands, footer)


def create_target_set_name(country_code: str) -> str:
    return f"country-{country_code}"


def create_temporary_set_name(country_code: str) -> str:
    return f"country-{country_code}.tmp-{time.strftime('%Y%m%d%H%M%S', time.gmtime())}"


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
