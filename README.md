# Zeroize

[![PyPI version](https://badge.fury.io/py/zeroize.svg)](https://badge.fury.io/py/zeroize)
[![PyPI](https://github.com/radumarias/zeroize-python/actions/workflows/PyPI.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/PyPI.yml)
[![tests](https://github.com/radumarias/zeroize-python/actions/workflows/tests.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/tests.yml)  

Securely clear secrets from memory. Built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood to zeroize and [libsodium-sys](https://crates.io/crates/libsodium-sys) for `mlock()` and `munlock()`. **Maximum you can mlock is 4MB**.  
It can work with `bytearray` and `numpy array`.

> [!WARNING]
> **In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process, see example below.  
> Also by itself it doesn't work if memory is moved or moved to swap. You can use `zeroize.mlock()` to lock the memory, see example below.**

# Examples

## Lock and zeroize memory

```python
"""By itself it doesn't work if memory is moved or moved to swap. You can use `crypes` with `libc.mlock()` to lock the memory"""

from zeroize import zeroize1, mlock, munlock
import numpy as np


if __name__ == "__main__":
    try:
        print("allocate memory")

        # regular array
        # Maximum you can mlock is 4MB
        arr = bytearray(b"1234567890")

        # numpy array
        # Maximum you can mlock is 4MB
        arr_np = np.array([0] * 10, dtype=np.uint8)
        arr_np[:] = arr
        assert arr_np.tobytes() == b"1234567890"

        print("locking memory")

        mlock(arr)
        mlock(arr_np)

        print("zeroize'ing...: ")
        zeroize1(arr)
        zeroize1(arr_np)

        print("checking if is zeroized")
        assert arr == bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        assert all(arr_np == 0)

        print("all good, bye!")

    finally:
        # Unlock the memory
        print("unlocking memory")
        munlock(arr)
        munlock(arr_np)
```

## Zeroing memory before forking child process

This mitigates the problems that appears on [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write). You need to zeroize the data before forking the child process.
```python
""" In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process. """

import os
from zeroize import zeroize1, mlock, munlock


if __name__ == "__main__":
    try:
        # Maximum you can mlock is 4MB
        sensitive_data = bytearray(b"Sensitive Information")
        mlock(sensitive_data)

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
        
        print("all good, bye!")

    finally:
        # Unlock the memory
        print("unlocking memory")
        munlock(sensitive_data)
```

# Build from source

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
pip install -r requirements.txt
maturin develop
python examples/lock_and_zeroize.py
python examples/zeroize_before_fork.py
```
