import numpy as np
import ctypes
from ctypes import wintypes

# Define the Windows API functions
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

VirtualLock = kernel32.VirtualLock
VirtualLock.restype = wintypes.BOOL
VirtualLock.argtypes = [wintypes.LPVOID, ctypes.c_size_t]

VirtualUnlock = kernel32.VirtualUnlock
VirtualUnlock.restype = wintypes.BOOL
VirtualUnlock.argtypes = [wintypes.LPVOID, ctypes.c_size_t]

SIZES_MB = [
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
    4
]

for size in SIZES_MB:
    print(f"size {size}")
    array_size = int(size * 1024 * 1024)
    array = np.zeros(array_size, dtype=np.uint8)  # Initialize array with zeros

    # Lock the memory associated with the array
    addr = array.ctypes.data
    size = array.nbytes

    if not VirtualLock(ctypes.c_void_p(addr), ctypes.c_size_t(size)):
        error_code = ctypes.get_last_error()
        error_message = ctypes.FormatError(error_code)
        print(f"VirtualLock failed with error code {error_code}: {error_message}")

    if not VirtualUnlock(ctypes.c_void_p(addr), ctypes.c_size_t(size)):
        error_code = ctypes.get_last_error()
        error_message = ctypes.FormatError(error_code)
        print(f"VirtualUnlock failed with error code {error_code}: {error_message}")
