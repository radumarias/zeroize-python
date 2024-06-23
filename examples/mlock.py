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

GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE

SetProcessWorkingSetSize = kernel32.SetProcessWorkingSetSize
SetProcessWorkingSetSize.restype = wintypes.BOOL
SetProcessWorkingSetSize.argtypes = [wintypes.HANDLE, ctypes.c_size_t, ctypes.c_size_t]

# Get the handle of the current process
current_process = GetCurrentProcess()

# Set the working set size
min_size = 256 * 1024  # Minimum working set size (e.g., 256KB)
max_size = 10 * 1024 * 1024  # Maximum working set size (e.g., 1024KB)

result = SetProcessWorkingSetSize(current_process, min_size, max_size)

if not result:
    error_code = ctypes.get_last_error()
    error_message = ctypes.FormatError(error_code)
    print(f"SetProcessWorkingSetSize failed with error code {error_code}: {error_message}")
else:
    print("SetProcessWorkingSetSize succeeded.")

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
