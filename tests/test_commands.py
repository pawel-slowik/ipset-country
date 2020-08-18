import ipaddress
import re
from typing import Iterable
from ipset import ipset_commands

TMP_SET_NAME_REGEXP = r"(?P<tmp_set_name>country-ZZ\.tmp-[a-zA-Z0-9]+)"


def test_output() -> None:

    def temporary_set_names(commands: Iterable[str], regexps: Iterable[str]) -> Iterable[str]:
        for command, regexp in zip(commands, regexps):
            match_dict = re.fullmatch(regexp, command).groupdict()
            if "tmp_set_name" in match_dict:
                yield match_dict["tmp_set_name"]

    expected = [
        "create -exist country-ZZ hash:net",
        "create TMP_SET_NAME_REGEXP hash:net",
        "add TMP_SET_NAME_REGEXP 127.0.0.0/24",
        "swap country-ZZ TMP_SET_NAME_REGEXP",
        "destroy TMP_SET_NAME_REGEXP",
    ]
    expected_regexps = [
        re.escape(expected_line).replace("TMP_SET_NAME_REGEXP", TMP_SET_NAME_REGEXP)
        for expected_line in expected
    ]

    output = list(ipset_commands("ZZ", [ipaddress.IPv4Network("127.0.0.0/24")]))

    assert len(output) == len(expected)
    for expected_regexp, output_line in zip(expected_regexps, output):
        assert re.fullmatch(expected_regexp, output_line)
    assert len(set(temporary_set_names(output, expected_regexps))) == 1


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
