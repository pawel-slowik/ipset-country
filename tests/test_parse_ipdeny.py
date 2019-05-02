import unittest
import ipaddress
from ipset import parse_ipdeny
from .util import open_test_file

class TestIpdeny(unittest.TestCase):

    def test_valid(self) -> None:
        with open_test_file("ipdeny/valid.zone") as text_input:
            self.assertEqual(
                list(parse_ipdeny(text_input)),
                [ipaddress.IPv4Network("127.0.0.0/24")]
            )

    def test_error(self) -> None:
        with open_test_file("ipdeny/invalid.zone") as text_input:
            with self.assertRaises(ValueError):
                list(parse_ipdeny(text_input))
