import unittest
from ipset import parse_ripestat
from .util import open_test_file

class TestRipestatErrorExplanations(unittest.TestCase):

    def test_explain_error_on_status_code(self) -> None:
        with open_test_file("ripestat/error_status_code.json") as json_input:
            with self.assertRaisesRegex(ValueError, "status_code=201"):
                parse_ripestat(json_input)

    def test_explain_error_on_status(self) -> None:
        with open_test_file("ripestat/error_status.json") as json_input:
            with self.assertRaisesRegex(ValueError, "status=not ok"):
                parse_ripestat(json_input)

    def test_explain_error_on_data_call_status(self) -> None:
        with open_test_file("ripestat/error_data_call_status.json") as json_input:
            with self.assertRaisesRegex(ValueError, "data_call_status.*deprecated"):
                parse_ripestat(json_input)

    def test_message_on_error(self) -> None:
        with open_test_file("ripestat/error_message.json") as json_input:
            with self.assertRaisesRegex(ValueError, "message=foo bar"):
                parse_ripestat(json_input)

    def test_messages_on_error(self) -> None:
        with open_test_file("ripestat/error_messages.json") as json_input:
            with self.assertRaisesRegex(ValueError, "(?s)message=foo.*bar"):
                parse_ripestat(json_input)
