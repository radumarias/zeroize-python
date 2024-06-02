import unittest
import zeroize
import numpy as np


class TestStringMethods(unittest.TestCase):

    def test_zeroize1(self):
        arr = bytearray(b"1234567890")
        zeroize.zeroize1(arr)
        self.assertEqual(arr, bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"))

    def test_zeroize_np(self):
        arr = np.array([0] * 10, dtype=np.uint8)
        arr[:] = bytes(b'1234567890')
        zeroize.zeroize_np(arr)
        self.assertEqual(True, all(arr == 0))


if __name__ == "__main__":
    unittest.main()
