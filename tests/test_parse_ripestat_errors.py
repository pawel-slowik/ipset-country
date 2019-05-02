import unittest
from ipset import parse_ripestat
from .util import open_test_file

class TestRipestatErrors(unittest.TestCase):

    def test_error_on_status_code(self) -> None:
        with open_test_file("ripestat/error_status_code.json") as json_input:
            with self.assertRaises(ValueError):
                parse_ripestat(json_input)

    def test_error_on_status(self) -> None:
        with open_test_file("ripestat/error_status.json") as json_input:
            with self.assertRaises(ValueError):
                parse_ripestat(json_input)

    def test_error_on_data_call_status(self) -> None:
        with open_test_file("ripestat/error_data_call_status.json") as json_input:
            with self.assertRaises(ValueError):
                parse_ripestat(json_input)

    def test_error_on_invalid_data(self) -> None:
        with open_test_file("ripestat/error_in_list.json") as json_input:
            with self.assertRaises(ValueError):
                list(parse_ripestat(json_input))
