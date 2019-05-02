import unittest
import ipaddress
from ipset import range_to_networks

class TestRangeToNetworks(unittest.TestCase):

    def test_invalid_empty(self) -> None:
        with self.assertRaises(ValueError):
            range_to_networks("")

    def test_invalid_format(self) -> None:
        with self.assertRaises(ValueError):
            range_to_networks("foo")

    def test_invalid_not_a_range(self) -> None:
        with self.assertRaises(ValueError):
            range_to_networks("127.0.0.1")

    def test_invalid_address_in_range(self) -> None:
        with self.assertRaises(ipaddress.AddressValueError):
            range_to_networks("127.0.0.1-127.0.0.256")

    def test_single_address_as_range(self) -> None:
        self.assertEqual(
            list(range_to_networks("192.168.10.1-192.168.10.1")),
            [ipaddress.IPv4Network("192.168.10.1/32")]
        )

    def test_class_c(self) -> None:
        self.assertEqual(
            list(range_to_networks("127.0.0.0-127.0.0.255")),
            [ipaddress.IPv4Network("127.0.0.0/24")]
        )

    def test_two_c_classes(self) -> None:
        self.assertEqual(
            list(range_to_networks("192.168.10.0-192.168.11.255")),
            [ipaddress.IPv4Network("192.168.10.0/23")]
        )

    def test_three_c_classes(self) -> None:
        self.assertEqual(
            list(range_to_networks("192.168.10.0-192.168.12.255")),
            [ipaddress.IPv4Network("192.168.10.0/23"), ipaddress.IPv4Network("192.168.12.0/24")]
        )
