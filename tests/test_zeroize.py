import unittest
from zeroize import zeroize1, mlock, munlock
import numpy as np


SIZES_MB = [
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
    4,
]


class TestStringMethods(unittest.TestCase):

    def test_zeroize1(self):
        try:
            arr = bytearray(b"1234567890")
            arr_np = np.array([0] * 10, dtype=np.uint8)
            mlock(arr)
            mlock(arr_np)
            zeroize1(arr)
            zeroize1(arr_np)
            self.assertEqual(
                arr, bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            )
            self.assertEqual(True, all(arr_np == 0))

        finally:
            munlock(arr)

    def test_zeroize1_sizes(self):
        for size in SIZES_MB:
            try:
                arr = bytearray(int(size * 1024 * 1024))
                arr_np = np.random.randint(
                    0, 256, int(size), dtype=np.uint8
                )
                print(f"Testing size: {size} MB")
                mlock(arr)
                mlock(arr_np)
                zeroize1(arr)
                zeroize1(arr_np)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))
                self.assertEqual(True, all(arr_np == 0))

            finally:
                munlock(arr)


if __name__ == "__main__":
    unittest.main()
