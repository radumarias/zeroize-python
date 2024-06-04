import unittest
import zeroize
import numpy as np
import ctypes
import platform


os_name = platform.system()

if os_name == "Linux":
    # Load the C standard library
    LIBC = ctypes.CDLL("libc.so.6")
elif os_name == "Darwin":
    # Load the C standard library
    LIBC = ctypes.CDLL("libc.dylib")
elif os_name == "Windows":
    # Load the kernel32 library
    kernel32 = ctypes.windll.kernel32
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")

if os_name == "Linux" or os_name == "Darwin":
    # Define mlock and munlock argument types
    MLOCK = LIBC.mlock
    MUNLOCK = LIBC.munlock

    # Define mlock and munlock argument types
    MLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    MUNLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
elif os_name == "Windows":
    # Define the VirtualLock and VirtualUnlock functions
    VirtualLock = kernel32.VirtualLock
    VirtualLock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    VirtualLock.restype = ctypes.c_int

    VirtualUnlock = kernel32.VirtualUnlock
    VirtualUnlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    VirtualUnlock.restype = ctypes.c_int
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")


def lock_memory(buffer):
    """Locks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
    size = len(buffer)
    if os_name == "Linux" or os_name == "Darwin":
        if MLOCK(address, size) != 0:
            raise RuntimeError("Failed to lock memory")
    elif os_name == "Windows":
        if VirtualLock(ctypes.addressof(buffer), ctypes.sizeof(buffer)) == 0:
            raise RuntimeError("VirtualLock failed")
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")


def unlock_memory(buffer):
    """Unlocks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buffer))
    size = len(buffer)
    if os_name == "Linux" or os_name == "Darwin":
        if MUNLOCK(address, size) != 0:
            raise RuntimeError("Failed to unlock memory")
    elif os_name == "Windows":
        if VirtualUnlock(ctypes.addressof(buffer), ctypes.sizeof(buffer)) == 0:
            raise RuntimeError("VirtualUnlock failed")
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")


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
            lock_memory(arr)
            arr[:] = bytes(b"1234567890")
            zeroize.zeroize_np(arr)
            self.assertEqual(True, all(arr == 0))

        finally:
            unlock_memory(arr)

    def test_zeroize1_sizes(self):
        for size in SIZES_MB:
            try:
                arr = bytearray(int(size * 1024 * 1024))
                lock_memory(arr)
                zeroize.zeroize1(arr)
                self.assertEqual(arr, bytearray(int(size * 1024 * 1024)))

            finally:
                unlock_memory(arr)

    def test_zeroize_np_sizes(self):
        for size in SIZES_MB:
            try:
                array_size = int(size * 1024 * 1024)
                random_array = np.random.randint(0, 256, array_size, dtype=np.uint8)
                lock_memory(random_array)
                zeroize.zeroize_np(random_array)
                self.assertEqual(True, all(random_array == 0))
            finally:
                unlock_memory(random_array)


if __name__ == "__main__":
    unittest.main()
