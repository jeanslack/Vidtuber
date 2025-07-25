# -*- coding: UTF-8 -*-

# Porpose: Contains test cases for the utils.py object.
# Rev: April.06.2020 *PEP8 compatible*

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from vidtuber.vt_utils.utils import (format_bytes,
                                         to_bytes,
                                         time_to_integer,
                                         integer_to_time,
                                         )
except ImportError as error:
    sys.exit(error)


class TestFormatBytes(unittest.TestCase):
    """Test case for the format_bytes function."""

    def test_format_bytes_bytes(self):
        self.assertEqual(format_bytes(518.00), "518.00B")

    def test_format_bytes_kilobytes(self):
        self.assertEqual(format_bytes(1024.00), "1.00KiB")

    def test_format_bytes_megabytes(self):
        self.assertEqual(format_bytes(1048576.00), "1.00MiB")

    def test_format_bytes_gigabytes(self):
        self.assertEqual(format_bytes(1073741824.00), "1.00GiB")

    def test_format_bytes_terabytes(self):
        self.assertEqual(format_bytes(1099511627776.00), "1.00TiB")


class TestToBytes(unittest.TestCase):
    """Test case for the to_bytes function."""

    def test_to_bytes_bytes(self):
        self.assertEqual(to_bytes("596.00B"), 596.00)
        self.assertEqual(to_bytes("133.55B"), 133.55)

    def test_to_bytes_kilobytes(self):
        self.assertEqual(to_bytes("1.00KiB"), 1024.00)
        self.assertEqual(to_bytes("5.55KiB"), 5683.20)

    def test_to_bytes_megabytes(self):
        self.assertEqual(to_bytes("13.64MiB"), 14302576.64)
        self.assertEqual(to_bytes("1.00MiB"), 1048576.00)

    def test_to_bytes_gigabytes(self):
        self.assertEqual(to_bytes("1.00GiB"), 1073741824.00)
        self.assertEqual(to_bytes("1.55GiB"), 1664299827.20)

    def test_to_bytes_terabytes(self):
        self.assertEqual(to_bytes("1.00TiB"), 1099511627776.00)


class TestTimeHuman(unittest.TestCase):
    """ Test case for the time_human function"""

    def test_to_human(self):
        self.assertEqual(integer_to_time(round(0.0 * 1000),
                                         mills=False), '00:00:00')
        self.assertEqual(integer_to_time(round(55.0 * 1000),
                                         mills=False), '00:00:55')
        self.assertEqual(integer_to_time(round(3023.0 * 1000),
                                         mills=False), '00:50:23')
        self.assertEqual(integer_to_time(round(9050.0 * 1000),
                                         mills=False), '02:30:50')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
