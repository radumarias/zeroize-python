import numpy as np
import platform
import random
import os
from zeroize import zeroize1, mlock, munlock


def setup_memory_limit():
    if not platform.system() == "Windows":
        return

    import ctypes
    from ctypes import wintypes

    # Define the Windows API functions
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    GetCurrentProcess = kernel32.GetCurrentProcess
    GetCurrentProcess.restype = wintypes.HANDLE

    SetProcessWorkingSetSize = kernel32.SetProcessWorkingSetSize
    SetProcessWorkingSetSize.restype = wintypes.BOOL
    SetProcessWorkingSetSize.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t]

    # Get the handle of the current process
    current_process = GetCurrentProcess()

    # Set the working set size
    min_size = 6 * 1024 * 1024  # Minimum working set size
    max_size = 10 * 1024 * 1024  # Maximum working set size

    result = SetProcessWorkingSetSize(current_process, min_size, max_size)

    if not result:
        error_code = ctypes.get_last_error()
        error_message = ctypes.FormatError(error_code)
        raise RuntimeError(f"SetProcessWorkingSetSize failed with error code {error_code}: {error_message}")

setup_memory_limit()

SIZES_MB = [
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.5,
    1,
    2,
    2.6
]

for size in SIZES_MB:
    try:
        arr = bytearray(int(size * 1024 * 1024))
        arr[:] = os.urandom(len(arr))
        arr_np = np.zeros(len(arr), dtype=np.uint8)
        arr_np[:] = arr
        print(f"Testing size: {size} MB")
        mlock(arr)
        mlock(arr_np)

        zeroize1(arr)
        zeroize1(arr_np)
        assert arr == bytearray(int(size * 1024 * 1024))
        assert all(arr_np == 0)

    finally:
        munlock(arr)
        munlock(arr_np)
