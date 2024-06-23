"""By itself it doesn't work if memory is moved or moved to swap. You can use `crypes` with `libc.mlock()` to lock the memory"""

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
