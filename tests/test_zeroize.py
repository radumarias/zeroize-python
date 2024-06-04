import unittest
from zeroize import zeroize1, zeroize_np, mlock, munlock, mlock_np, munlock_np
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
    8,
    16,
    32,
    64,
    128,
]


class TestStringMethods(unittest.TestCase):

    def test_zeroize1(self):
        try:
            arr = bytearray(b"1234567890")
            mlock(arr)
            zeroize1(arr)
            self.assertEqual(
                arr, bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            )

        finally:
            munlock(arr)

    def test_zeroize_np(self):
        try:
            arr = np.array([0] * 10, dtype=np.uint8)
            mlock_np(arr)
            arr[:] = bytes(b"1234567890")
            zeroize_np(arr)
            self.assertEqual(True, all(arr == 0))

        finally:
            munlock_np(arr)

    def test_zeroize1_sizes(self):
        for size in SIZES_MB:
            try:
                arr = bytearray(int(size * 1024 * 1024))
                mlock(arr)
                zeroize1(arr)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))

            finally:
                munlock(arr)

    def test_zeroize_np_sizes(self):
        for size in SIZES_MB:
            try:
                array_size = int(size * 1024 * 1024)
                random_array = np.random.randint(0, 256, array_size, dtype=np.uint8)
                mlock_np(random_array)
                zeroize_np(random_array)
                self.assertEqual(True, all(random_array == 0))
            finally:
                munlock_np(random_array)


if __name__ == "__main__":
    unittest.main()
