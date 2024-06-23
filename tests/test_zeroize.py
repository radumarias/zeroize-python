import unittest
from zeroize import zeroize1, mlock, munlock
import numpy as np
import os
import array
import random
import ctypes
import platform
import sys


# Functions for locking and unlocking memory
def lock_memory(address, size):
    if platform.system() == 'Linux':
        # On Linux, use mlock
        libc = ctypes.CDLL('libc.so.6')
        if libc.mlock(address, size) != 0:
            raise RuntimeError("Failed to lock memory")
    elif platform.system() == 'Windows':
        # On Windows, use VirtualLock
        if not ctypes.windll.kernel32.VirtualLock(address, size):
            raise RuntimeError("Failed to lock memory")
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")

def unlock_memory(address, size):
    if platform.system() == 'Linux':
        # On Linux, use munlock
        libc = ctypes.CDLL('libc.so.6')
        if libc.munlock(address, size) != 0:
            raise RuntimeError("Failed to unlock memory")
    elif platform.system() == 'Windows':
        # On Windows, use VirtualUnlock
        if not ctypes.windll.kernel32.VirtualUnlock(address, size):
            raise RuntimeError("Failed to unlock memory")
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")


SIZES_MB = [
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
#     2.97,
    4,
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
#                 mlock(arr)
#                 print("mlock np array")
#                 mlock(arr_np)
#                 print("mlock array.array")
#                 mlock(arr2)

                address = (ctypes.c_char * len(arr)).from_buffer(arr)
                size = len(arr)

                address2 = arr2.buffer_info()[0]
                size2 = arr2.buffer_info()[1] * arr2.itemsize
                print("address2 {address2}")
                print("size2 {size2}")

                print("lock arr")
                lock_memory(address, size)
                print("lock arr2")
                lock_memory(address2, size2)

                if not VirtualLock(ctypes.c_void_p(buffer_address), ctypes.c_size_t(buffer_size)):
                    raise RuntimeError("Failed to lock memory")

                if not VirtualUnlock(ctypes.c_void_p(buffer_address), ctypes.c_size_t(buffer_size)):
                    raise RuntimeError("Failed to unlock memory")

                if not VirtualLock(ctypes.c_void_p(buffer_address2), ctypes.c_size_t(buffer_size2)):
                    raise RuntimeError("Failed to lock memory")

                if not VirtualUnlock(ctypes.c_void_p(buffer_address2), ctypes.c_size_t(buffer_size2)):
                    raise RuntimeError("Failed to unlock memory")

                zeroize1(arr)
                zeroize1(arr_np)
                zeroize1(arr2)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))
                self.assertEqual(True, all(arr_np == 0))
                self.assertEqual(True, all(byte == 0 for byte in arr2))

            finally:
                print("f")
#                 munlock(arr)


if __name__ == "__main__":
    unittest.main()
