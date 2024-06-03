"""By itself it doesn't work if memory is moved or moved to swap. You can use `crypes` with `libc.mlock()` to lock the memory"""

from zeroize import zeroize1, zeroize_np
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


try:
    print("allocate memory")

    # regular array
    arr = bytearray(b"1234567890")

    # numpy array
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
