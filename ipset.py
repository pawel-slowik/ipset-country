#!/usr/bin/env python3

import ipaddress
import itertools
import json
import urllib.parse
import codecs
import time
import http.client
from http import HTTPStatus
from typing import Iterable, Mapping, Type, IO, Optional

def list_ipdeny(country_code: str) -> Iterable[ipaddress.IPv4Network]:
    return parse_ipdeny(open_url(get_ipdeny_url(country_code)))

def get_ipdeny_url(country_code: str) -> str:
    return "http://www.ipdeny.com/ipblocks/data/aggregated/%s-aggregated.zone" % country_code

def parse_ipdeny(text_input: IO[bytes]) -> Iterable[ipaddress.IPv4Network]:
    return (
        ipaddress.IPv4Network(input_network.decode("ascii").strip())
        for input_network in text_input
    )

def list_ripestat(country_code: str) -> Iterable[ipaddress.IPv4Network]:
    networks = parse_ripestat(open_url(get_ripestat_url(country_code)))
    # RIPEstat data is not aggregated, needs collapsing
    networks = ipaddress.collapse_addresses(networks)
    return networks

def get_ripestat_url(country_code: str) -> str:
    return "https://stat.ripe.net/data/country-resource-list/data.json?resource=%s" % country_code

def parse_ripestat(json_input: IO[bytes]) -> Iterable[ipaddress.IPv4Network]:

    def error_message(error_response: Mapping) -> Optional[str]:
        if "message" in error_response:
            return str(response["message"])
        if "messages" in error_response:
            return "\n".join(error_response["messages"])
        return None

    ascii_reader = codecs.getreader("ascii") # json.load doesn't support bytes in Python < 3.6
    response = json.load(ascii_reader(json_input))
    if response["status_code"] != HTTPStatus.OK or response["status"] != "ok":
        raise ValueError(
            "error in RIPEstat response: status_code=%s, status=%s, message=%s" % (
                response["status_code"],
                response["status"],
                error_message(response),
            )
        )
    if not response["data_call_status"].startswith("supported"):
        raise ValueError("unexpected RIPEstat data_call_status: %s" % response["data_call_status"])
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

def open_url(url: str) -> IO[bytes]:

    def connection_class(scheme: str) -> Type[http.client.HTTPConnection]:
        scheme_class_map = {
            "http": http.client.HTTPConnection,
            "https": http.client.HTTPSConnection,
        }
        return scheme_class_map[scheme.lower()]

    def url_without_netloc(url: str) -> str:
        split = urllib.parse.urlsplit(url)
        return urllib.parse.urlunsplit(("", "", split.path, split.query, split.fragment))

    parts = urllib.parse.urlparse(url)
    connection = connection_class(parts.scheme)(parts.netloc)
    connection.request("GET", url_without_netloc(url))
    response = connection.getresponse()
    if response.status != HTTPStatus.OK:
        raise ValueError("unexpected HTTP code: %d" % response.status)
    return response

def range_to_networks(network_range: str) -> Iterable[ipaddress.IPv4Network]:
    parts = network_range.split("-")
    if len(parts) != 2:
        raise ValueError
    first = ipaddress.IPv4Address(parts[0])
    last = ipaddress.IPv4Address(parts[1])
    return ipaddress.summarize_address_range(first, last)

def list_networks(country_code: str, max_diff: int = 0) -> Iterable[ipaddress.IPv4Network]:
    ipdeny_networks = set(list_ipdeny(country_code))
    ripestat_networks = set(list_ripestat(country_code))
    if ipdeny_networks == ripestat_networks:
        return ipdeny_networks
    messages = []
    ripestat_missing = ipdeny_networks - ripestat_networks
    if ripestat_missing:
        messages.append("networks present in IPdeny but not in RIPEstat: %s" % ripestat_missing)
    ipdeny_missing = ripestat_networks - ipdeny_networks
    if ipdeny_missing:
        messages.append("networks present in RIPEstat but not in IPdeny: %s" % ipdeny_missing)
    if len(ripestat_missing) + len(ipdeny_missing) > max_diff:
        raise ValueError("\n".join(messages))
    return ipdeny_networks & ripestat_networks

def ipset(country_code: str, max_diff: int = 0) -> Iterable[str]:
    # set name must be shorter than 32 characters
    set_name = "country-%s" % country_code
    tmp_set_name = "country-%s.tmp-%s" % (
        country_code,
        time.strftime("%Y%m%d%H%M%S", time.gmtime()),
    )
    header = (
        "create -exist %s hash:net" % set_name,
        "create %s hash:net" % tmp_set_name,
    )
    footer = (
        "swap %s %s" % (set_name, tmp_set_name),
        "destroy %s" % tmp_set_name,
    )
    commands = (
        "add %s %s" % (tmp_set_name, network)
        for network in sorted(list_networks(country_code, max_diff))
    )
    return itertools.chain(header, commands, footer)

def main() -> None:
    import argparse
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
