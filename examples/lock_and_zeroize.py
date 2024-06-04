"""By itself it doesn't work if memory is moved or moved to swap. You can use `crypes` with `libc.mlock()` to lock the memory"""

from zeroize import zeroize1, zeroize_np
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
        if VirtualLock(address, size) == 0:
            raise RuntimeError("Failed to lock memory")
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
        if VirtualUnlock(address, size) == 0:
            raise RuntimeError("Failed to unlock memory")
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")


if __name__ == "__main__":
    try:
        print("allocate memory")

        # regular array
        # max size you can lock is 4MB, at least on Linux
        arr = bytearray(b"1234567890")

        # numpy array
        # max size you can lock is 4MB, at least on Linux
        arr_np = np.array([0] * 10, dtype=np.uint8)
        arr_np[:] = arr
        assert arr_np.tobytes() == b"1234567890"

        print("locking memory")

        lock_memory(arr)
        lock_memory(arr_np)

        print("zeroize'ing...: ")
        zeroize1(arr)
        zeroize_np(arr_np)

        print("checking if is zeroized")
        assert arr == bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        assert all(arr_np == 0)

        print("all good, bye!")

    finally:
        # Unlock the memory
        print("unlocking memory")
        unlock_memory(arr)
        unlock_memory(arr_np)
