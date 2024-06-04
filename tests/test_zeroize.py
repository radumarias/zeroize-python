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
    # Load necessary libraries
    kernel32 = ctypes.windll.kernel32
    ntdll = ctypes.windll.ntdll

    # Define NtLockVirtualMemory and NtUnlockVirtualMemory
    NtLockVirtualMemory = ntdll.NtLockVirtualMemory
    NtUnlockVirtualMemory = ntdll.NtUnlockVirtualMemory
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")

if os_name == "Linux" or os_name == "Darwin":
    # Define mlock and munlock argument types
    MLOCK = LIBC.mlock
    MUNLOCK = LIBC.munlock

    # Define mlock and munlock argument types
    MLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    MUNLOCK.argtypes = [ctypes.c_void_p, ctypes.c_size_t]


def lock_memory(buf):
    """Locks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buf))
    size = len(buf)
    if os_name == "Linux" or os_name == "Darwin":
        if MLOCK(address, size) != 0:
            raise RuntimeError("Failed to lock memory")
    elif os_name == "Windows":
        buf_ptr = ctypes.c_void_p(ctypes.addressof(ctypes.c_char.from_buffer(buf)))
        size = ctypes.c_size_t(len(buf))
        region_size = ctypes.c_size_t(size.value)
        status = NtLockVirtualMemory(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(buf_ptr), ctypes.byref(region_size), 0
        )
        if status != 0:
            raise RuntimeError(f"NtLockVirtualMemory failed with status code: {status}")
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")


def unlock_memory(buf):
    """Unlocks the memory of the given buffer."""
    address = ctypes.addressof(ctypes.c_char.from_buffer(buf))
    size = len(buf)
    if os_name == "Linux" or os_name == "Darwin":
        if MUNLOCK(address, size) != 0:
            raise RuntimeError("Failed to unlock memory")
    elif os_name == "Windows":
        buf_ptr = ctypes.c_void_p(ctypes.addressof(ctypes.c_char.from_buffer(buf)))
        size = ctypes.c_size_t(len(buf))
        region_size = ctypes.c_size_t(size.value)
        status = NtUnlockVirtualMemory(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(buf_ptr), ctypes.byref(region_size), 0
        )
        if status != 0:
            raise RuntimeError(f"NtUnlockVirtualMemory failed with status code: {status}")
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
