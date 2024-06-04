""" In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process. """

import os
from zeroize import zeroize1
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
        # max size you can lock is 4MB, at least on Linux
        sensitive_data = bytearray(b"Sensitive Information")
        lock_memory(sensitive_data)

        print("Before zeroization:", sensitive_data)

        zeroize1(sensitive_data)
        print("After zeroization:", sensitive_data)

        # Forking after zeroization to ensure no sensitive data is copied
        pid = os.fork()
        if pid == 0:
            # This is the child process
            print("Child process memory after fork:", sensitive_data)
        else:
            # This is the parent process
            os.wait()  # Wait for the child process to exit

    finally:
        # Unlock the memory
        print("unlocking memory")
        unlock_memory(sensitive_data)
