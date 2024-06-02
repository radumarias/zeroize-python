import zeroize
import numpy as np


# regular array
arr = bytearray(b'1234567890')

# numpy array
arr_np = np.array([0] * 10, dtype=np.uint8)
arr_np[:] = arr
assert arr_np.tobytes() == b'1234567890'

print("zeroize'ing...: ")
zeroize.zeroize1(arr)
zeroize.zeroize_np(arr_np)

print("checking if is zeroized...")
assert arr == bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
assert all(arr_np == 0)

print("all good, bye!")
