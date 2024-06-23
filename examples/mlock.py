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

# Create a numpy array
array = np.random.rand(1000000)  # Example: 1 million double-precision floats

# Lock the memory associated with the array
addr = array.ctypes.data
size = array.nbytes

if not VirtualLock(ctypes.c_void_p(addr), ctypes.c_size_t(size)):
    raise ctypes.WinError(ctypes.get_last_error())

print("Memory locked successfully.")

# ... perform operations on the array ...

# Unlock the memory when done
if not VirtualUnlock(ctypes.c_void_p(addr), ctypes.c_size_t(size)):
    raise ctypes.WinError(ctypes.get_last_error())

print("Memory unlocked successfully.")
