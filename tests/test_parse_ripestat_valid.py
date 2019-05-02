import unittest
import ipaddress
from ipset import parse_ripestat
from .util import open_test_file

class TestRipestatValid(unittest.TestCase):

    def test_valid(self) -> None:
        with open_test_file("ripestat/valid.json") as json_input:
            self.assertEqual(
                list(parse_ripestat(json_input)),
                [ipaddress.IPv4Network("127.0.0.0/24")]
            )
