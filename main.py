import zeroize
import numpy as np
import ctypes


# Lock memory using ctypes
def lock_memory():
    libc = ctypes.CDLL("libc.so.6")
    # Lock all current and future pages from being swapped out
    libc.mlockall(ctypes.c_int(0x02 | 0x04))  # MCL_CURRENT | MCL_FUTURE


def unlock_memory():
    libc = ctypes.CDLL("libc.so.6")
    # Unlock all locked pages
    libc.munlockall()


print("locking memory")
lock_memory()

print("allocate memory")

# regular array
arr = bytearray(b"1234567890")

# numpy array
arr_np = np.array([0] * 10, dtype=np.uint8)
arr_np[:] = arr
assert arr_np.tobytes() == b"1234567890"

print("zeroize'ing...: ")
zeroize.zeroize1(arr)
zeroize.zeroize_np(arr_np)

print("checking if is zeroized")
assert arr == bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
assert all(arr_np == 0)

print("unlocking memory")
unlock_memory()

print("all good, bye!")
