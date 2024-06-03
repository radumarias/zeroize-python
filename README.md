# Zeroize

[![PyPI version](https://badge.fury.io/py/zeroize.svg)](https://badge.fury.io/py/zeroize)
[![PyPI](https://github.com/radumarias/zeroize-python/actions/workflows/PyPI.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/PyPI.yml)
[![tests](https://github.com/radumarias/zeroize-python/actions/workflows/tests.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/tests.yml)  

Clear secrets from memory. Built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.
Uses a portable pure Rust implementation that works everywhere.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood.  
It can work with `bytearray` and `numpy array`.

> [!WARNING]
> **In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process, see example below.  
> Also by itself it doesn't work if memory is moved or moved to swap. You can use `crypes` with `libc.mlock()` to lock the memory, see example below.**

# Examples

## Lock and zeroize memory

```python
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
```

## Zeroing memory before starting child process

This mitigates the problems that appears on [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write). You need to zeroize the data before forking the child process.
```python
import os
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
```

# Building from source

## Browser

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/radumarias/zeroize-python)

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new/?repo=radumarias%2Fzeroize-python&ref=main)

## Geting sources from GitHub
Skip this if you're starting it in browser.

```bash
git clone https://github.com/radumarias/zeroize-python && cd zeroize-python
```

## Compile and run

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
To configure your current shell, you need to source
the corresponding env file under $HOME/.cargo.
This is usually done by running one of the following (note the leading DOT):
```bash
. "$HOME/.cargo/env"
```
```
python -m venv .env
source .env/bin/activate
pip install maturin
pip install numpy
maturin develop
python examples/lock_and_zeroize.py
python examples/zeroize_before_fork.py
```
