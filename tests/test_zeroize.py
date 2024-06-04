import unittest
import zeroize
import numpy as np


import ctypes


# Load the C standard library
LIBC = ctypes.CDLL("libc.so.6")
MLOCK = LIBC.mlock
MUNLOCK = LIBC.munlock

# Define mlock and munlock argument types
MLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
MUNLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]


def lock_memory(buffer):
    """Locks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
    size = len(buffer)
    if MLOCK(address, size) != 0:
        raise RuntimeError("Failed to lock memory")


def unlock_memory(buffer):
    """Unlocks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
    size = len(buffer)
    if MUNLOCK(address, size) != 0:
        raise RuntimeError("Failed to unlock memory")


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
        try:
            arr = bytearray(b"1234567890")
            lock_memory(arr)
            zeroize.zeroize1(arr)
            self.assertEqual(
                arr, bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            )

        finally:
            unlock_memory(arr)

    def test_zeroize_np(self):
        try:
            arr = np.array([0] * 10, dtype=np.uint8)
            arr[:] = bytes(b"1234567890")
            zeroize.zeroize_np(arr)
            self.assertEqual(True, all(arr == 0))

        finally:
            unlock_memory(arr)

    def test_zeroize1_sizes(self):
        for size in SIZES_MB:
            try:
                arr = bytearray(int(size * 1024 * 1024))
                zeroize.zeroize1(arr)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))

            finally:
                unlock_memory(arr)

    def test_zeroize_np_sizes(self):
        for size in [size for size in SIZES_MB if size < 4]:
            try:
                array_size = int(size * 1024 * 1024)
                random_array = np.random.randint(0, 256, array_size, dtype=np.uint8)
                zeroize.zeroize_np(random_array)
                self.assertEqual(True, all(random_array == 0))
            finally:
                unlock_memory(random_array)


if __name__ == "__main__":
    unittest.main()
