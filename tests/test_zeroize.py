import unittest
from zeroize import zeroize1, mlock, munlock
import numpy as np
import os
import array
import random
import ctypes


SIZES_MB = [
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
    2.97,
]


class TestStringMethods(unittest.TestCase):

    def test_zeroize1(self):
        try:
            arr = bytearray(b"1234567890")
            arr_np = np.array([0] * 10, dtype=np.uint8)
            arr_np[:]=arr
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
                arr[:] = os.urandom(len(arr))
                arr_np = np.zeros(len(arr), dtype=np.uint8)
                arr_np[:] = arr
                arr2 = array.array('B', (random.randint(0, 255) for _ in range(int(size * 1024 * 1024))))
                print(f"Testing size: {size} MB")
#                 print("mlock bytearray")
                mlock(arr)
#                 print("mlock np array")
#                 mlock(arr_np)
#                 print("mlock array.array")
#                 mlock(arr2)

                buffer_address = arr2.buffer_info()[0]
                buffer_size = arr2.buffer_info()[1] * arr2.itemsize

                # Define VirtualLock function from kernel32.dll
                VirtualLock = ctypes.windll.kernel32.VirtualLock
                VirtualLock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
                VirtualLock.restype = ctypes.c_bool

                if VirtualLock(ctypes.c_void_p(buffer_address), ctypes.c_size_t(buffer_size)):
                    print("Memory locked")
                else:
                    print("Failed to lock memory")

                zeroize1(arr)
                zeroize1(arr_np)
                zeroize1(arr2)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))
                self.assertEqual(True, all(arr_np == 0))
                self.assertEqual(True, all(byte == 0 for byte in arr2))

            finally:
                munlock(arr)


if __name__ == "__main__":
    unittest.main()
