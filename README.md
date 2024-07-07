# zeroize

[![PyPI version](https://badge.fury.io/py/zeroize.svg)](https://badge.fury.io/py/zeroize)
[![CI](https://github.com/radumarias/zeroize-python/actions/workflows/CI.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/CI.yml)

Securely clear secrets from memory. Built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood to zeroize and [memsec](https://crates.io/crates/memsec) for `mlock()` and `munlock()`. **Maximum you can mlock is 2662 KB**.  
It can work with `bytearray` and `numpy array`.

> [!WARNING]  
> **In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process, see example below.  
> Also by itself it doesn't work if memory is moved or moved to swap. You can use `zeroize.mlock()` to lock the memory, see example below.**

# Caveats of `mlock()`

`mlock` works on pages, so two variables could reside in the same page and if you `munlock` one it will `munlock` the whole page and also the memory for the other variable.
 Ideally you could `munlock` all your vars at same time so it would not be affected by the overlap. One strategy could be to expire your vars that store credentials when not used and to reload them again when needed. Like that you could `mlock` when you load them and `munlock` on expire and keep all vars under the same expire policy. Like this all var will be `munlock`ed at the same time.

# Examples

**On Windows you can mlock up to 128 KB by default. If you need more you need to first call `SetProcessWorkingSetSize` to increase the `dwMinimumWorkingSetSize`. Will have an example below.**

## Lock and zeroize memory

```python
from zeroize import zeroize1, mlock, munlock
import numpy as np


if __name__ == "__main__":
    try:
        print("allocate memory")

        # regular array
        # Maximum you can mlock is 2662 KB
        arr = bytearray(b"1234567890")

        # numpy array
        # Maximum you can mlock is 2662 KB
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
import os
from zeroize import zeroize1, mlock, munlock


if __name__ == "__main__":
    try:
        # Maximum you can mlock is 2662 KB
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

# Locking more than 128 KB

On Windows if you need to `mlock` more than `128 KB` you need to first call `SetProcessWorkingSetSize` to increase the `dwMinimumWorkingSetSize`.

Here is an example, set `min_size` to the size you want to `mlock` + some overhead.

```python
import platform


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

# Call this before you mlock
setup_memory_limit()
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

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
maturin develop
pytest
python examples/lock_and_zeroize.py
python examples/zeroize_before_fork.py
python examples/mlock.py
```

# Contribute

Feel free to fork it, change and use it in any way that you want. If you build something interesting and feel like sharing pull requests are always appreciated.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache License, shall be dual-licensed as above, without any additional terms or conditions.

## How to contribute

1. Fork the repo
2. Make the changes in your fork
3. Add tests for your changes, if applicable
4. `cargo build --workspace --all-targets --all-features` and fix any issues
5. `cargo fmt --all`, you can configure your IDE to do this on
   save [RustRover](https://www.jetbrains.com/help/rust/rustfmt.html)
   and [VSCode](https://code.visualstudio.com/docs/languages/rust#_formatting)
6. `cargo check --workspace --all-targets` and fix any errors and warnings
7. `cargo clippy --all-targets` and fix any errors
8. `cargo test --all-targets --all-features` and fix any issues
9. Create a PR
10. Monitor the checks (GitHub actions run)
11. Respond to any comments
12. In the end ideally it will be merged to `main`
