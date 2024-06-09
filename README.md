# zeroize

[![PyPI version](https://badge.fury.io/py/zeroize.svg)](https://badge.fury.io/py/zeroize)
[![CI](https://github.com/radumarias/zeroize-python/actions/workflows/CI.yml/badge.svg)](https://github.com/radumarias/zeroize-python/actions/workflows/CI.yml)

Securely clear secrets from memory. Built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood to zeroize and [memsec](https://crates.io/crates/memsec) for `mlock()` and `munlock()`. **Maximum you can mlock is 4MB**.  
It can work with `bytearray` and `numpy array`.

> [!WARNING]  
> **In the case of [Copy-on-write fork](https://en.wikipedia.org/wiki/Copy-on-write) you need to zeroize the memory before forking the child process, see example below.  
> Also by itself it doesn't work if memory is moved or moved to swap. You can use `zeroize.mlock()` to lock the memory, see example below.**

# Caveats of `mlock()`

`mlock` works on pages, so 2 variables could reside in the same page and if you `munlock` one it will `munlock` the whole page and also the memory for the other variable. Ideally you could `munlock` all your vars at same time so it would not be affected by the overlap. One strategy could be to expire your vars that store credentials when not used and to reload them again when needed. Like that you could `mlock` when you load them and `munlock` on expire and keep all vars under the same expire policy. Like this all var will be `munlock`ed at the same time.

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

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
maturin develop
python examples/lock_and_zeroize.py
python examples/zeroize_before_fork.py
```

# Contribute

Feel free to fork it, change and use it in any way that you want. If you build something interesting and feel like sharing pull requests are always appreciated.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache License, shall be dual-licensed as above, without any additional terms or conditions.

## How to contribute

1. Fork the repo
2. Make the changes in your fork
3. Add tests for your changes, if applicable
4. `RUSTFLAGS: "-Dwarnings"` set this before you run `cargo` commands, one time per terminal or add it to your `rc` file
5. `cargo build --all --all-features` and fix any issues
6. `cargo fmt --all`, you can cnofigure your IDE to do this on save [RustRover](https://www.jetbrains.com/help/rust/rustfmt.html) and [VSCode](https://code.visualstudio.com/docs/languages/rust#_formatting)
7. `cargo check --all --all-features` and fix any errors and warnings
8. `cargo clippy --all --all-features` and fix any errors
9. `cargo test --all --all-features` and fix any issues
10. `cargo bench --all --all-features` and fix any issues
11. Create a PR
12. Monitor the checks (GitHub actions runned)
13. Respond to any comments
14. In the end ideally it will be merged to `main`
