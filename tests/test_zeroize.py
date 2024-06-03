import ctypes
import os
import unittest
import zeroize
import numpy as np


# Lock memory using ctypes
def lock_memory():
    libc = ctypes.CDLL("libc.so.6")
    # Lock all current and future pages from being swapped out
    libc.mlockall(ctypes.c_int(0x02 | 0x04))  # MCL_CURRENT | MCL_FUTURE


def unlock_memory():
    libc = ctypes.CDLL("libc.so.6")
    # Unlock all locked pages
    libc.munlockall()


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
    256,
    512,
    1024,
    2 * 1024,
    4 * 1024,
]


class TestStringMethods(unittest.TestCase):

    def test_zeroize1(self):
        lock_memory()

        arr = bytearray(b"1234567890")
        zeroize.zeroize1(arr)
        self.assertEqual(arr, bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"))

        unlock_memory()

    def test_zeroize_np(self):
        lock_memory()

        arr = np.array([0] * 10, dtype=np.uint8)
        arr[:] = bytes(b"1234567890")
        zeroize.zeroize_np(arr)
        self.assertEqual(True, all(arr == 0))

        unlock_memory()

    def test_zeroize1_sizes(self):
        # lock_memory()

        for size in SIZES_MB:
            arr = bytearray(int(size * 1024 * 1024))
            zeroize.zeroize1(arr)
            self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))
        
        # unlock_memory()

    def test_zeroize_np_sizes(self):
        # lock_memory()

        for size in [size for size in SIZES_MB if size < 4]:
            array_size = int(size * 1024 * 1024)
            random_array = np.random.randint(0, 256, array_size, dtype=np.uint8)
            zeroize.zeroize_np(random_array)
            self.assertEqual(True, all(random_array == 0))
        
        # unlock_memory()


if __name__ == "__main__":
    unittest.main()
