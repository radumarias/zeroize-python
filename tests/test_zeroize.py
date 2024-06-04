import unittest
from zeroize import zeroize1, zeroize_np, mlock, munlock, mlock_np, munlock_np
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
    # Define constants
    PAGE_READWRITE = 0x04
    MEM_COMMIT = 0x1000
    MEM_RESERVE = 0x2000
    
    # Load kernel32 library
    kernel32 = ctypes.windll.kernel32
    
    # Enable the SeLockMemoryPrivilege privilege
    def enable_lock_memory_privilege():
        TOKEN_ADJUST_PRIVILEGES = 0x0020
        TOKEN_QUERY = 0x0008
        SE_PRIVILEGE_ENABLED = 0x0002
        privilege_name = "SeLockMemoryPrivilege"

        class LUID(ctypes.Structure):
            _fields_ = [("LowPart", ctypes.c_uint32), ("HighPart", ctypes.c_int32)]

        class LUID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Luid", LUID), ("Attributes", ctypes.c_uint32)]

        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", ctypes.c_uint32), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

        # Open process token
        token_handle = ctypes.c_void_p()
        if not kernel32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token_handle)):
            raise ctypes.WinError()

        # Lookup privilege value
        luid = LUID()
        if not kernel32.LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid)):
            raise ctypes.WinError()

        # Adjust token privileges
        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

        if not kernel32.AdjustTokenPrivileges(token_handle, False, ctypes.byref(tp), ctypes.sizeof(tp), None, None):
            raise ctypes.WinError()

        # Close the token handle
        kernel32.CloseHandle(token_handle)        
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
        size = ctypes.sizeof(ctypes.c_char) * len(buf)
        if not kernel32.VirtualLock(buf_ptr, size):
            raise RuntimeError("VirtualLock failed")
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
        size = ctypes.sizeof(ctypes.c_char) * len(buf)
        if not kernel32.VirtualUnlock(buf_ptr, size):
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
    # if os_name == "Windows":
        # # Enable the privilege to lock memory
        # enable_lock_memory_privilege()
        
    unittest.main()
