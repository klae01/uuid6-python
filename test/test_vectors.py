import unittest
from unittest.mock import patch

from uuid6 import UUID, uuid6, uuid7


class TestVectors(unittest.TestCase):
    """
    https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format-03#appendix-B
    """

    @patch("uuid6._last_v6_timestamp", 1)
    @patch("secrets.randbits", return_value=0x9E6BDECED846)
    @patch("time.time_ns", return_value=0x16D6320C3D4DCC00)
    def test_uuid6_hex_from_time(self, mocktime, mockrand):
        uuid_6 = uuid6(0xB3C8)
        self.assertEqual(str(uuid_6), "1ec9414c-232a-6b00-b3c8-9e6bdeced846")

    @patch("uuid6._last_v7_timestamp", 1)
    @patch("time.time_ns", return_value=0x17F21CFD130 * 10**6)
    def test_uuid7_hex_from_time(self, mocktime):
        uuid_7 = uuid7()
        self.assertEqual(str(uuid_7)[:15], "017f21cf-d130-7")

    def test_uuid6_time_from_hex(self):
        uuid_6 = UUID(hex="1EC9414C-232A-6B00-B3C8-9E6BDECED846")
        self.assertEqual(uuid_6.time, 138648505420000000)
        uuid_1 = UUID(hex="C232AB00-9414-11EC-B3C8-9E6BDECED846")
        self.assertEqual(uuid_6.time, uuid_1.time)

    def test_uuid7_time_from_hex(self):
        uuid_7 = UUID(hex="017F21CF-D130-7CC3-98C4-DC0C0C07398F")
        self.assertEqual(uuid_7.time // 10**6, 1645539742000)


if __name__ == "__main__":
    unittest.main()
