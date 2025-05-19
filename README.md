![Build Status][build-badge]
[![Coverage][coverage-badge]][coverage-url]

[build-badge]: https://github.com/pawel-slowik/ipset-country/workflows/tests/badge.svg
[coverage-badge]: https://codecov.io/gh/pawel-slowik/ipset-country/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/pawel-slowik/ipset-country

Generate country based [IP sets](http://ipset.netfilter.org/) for packet
filtering in the Linux kernel.

## Example usage

	./ipset.py -h
	./ipset.py cn | sudo ipset restore
	sudo iptables -A INPUT -m set --match-set country-cn-v4 src -j REJECT
	sudo ip6tables -A INPUT -m set --match-set country-cn-v6 src -j REJECT

Included is an [Ansible](https://www.ansible.com/) playbook that can be used to
set up multiple hosts with the same rules.

    for country in $(yq -r '.countries[]' < ansible/vars.yaml); do ./ipset.py "$country" > "ipset-$country.txt"; done
    ansible-playbook ansible/update.yaml

## Installation

The script is not packaged. If you want to use it, clone or download this
repository. The only requirement is Python 3.x (no external packages).

## Features

There are plenty of blog posts / tutorials / gists on this subject. So why yet
another `ipset` generator?

Here are some features unique to this script:

- Validate input. Don't blindly shell-execute `sudo whatever $IP`, where `$IP`
  is neither quoted nor escaped and could be any shell construct.

- Compare data from two (hopefully) independent sources:
	- [IPdeny](http://www.ipdeny.com/ipblocks/)
	- [RIPEstat Data API](https://stat.ripe.net/docs/data_api#country-resource-list)

  By default, if there's a mismatch between the two sources, an error message is
  displayed and the set is not generated. You can opt to ignore a limited number
  of differences by using the `-i` parameter. Sets generated in this manner
  contain only networks that are present in both data sources.

- Generate a list of commands (a session) that can be fed into `ipset restore`
  instead of directly executing `ipset`. This has several advantages:
	- the generator script doesn't need root privileges,
	- the generated file can be put under version control, diff-reviewed
	  and redistributed to many servers,
	- a single `ipset restore` call is a lot faster than thousands of
	  `ipset add` calls.

- Fail safely on errors. If a generated command fails while replacing an
  existing set, the original set will not be modified. In that case, you may
  have to manually delete a temporary set named
  `country-$COUNTRYCODE.tmp-$GMTDATETIME`.

- Don't change `iptables` rules, only generate the IP set. This makes it easier
  to generate sets for various contexts (for blacklisting or for whitelisting,
  for separate servers etc.).

- The script is an importable Python module, which means it can be easily
  integrated with other Python based solutions.
