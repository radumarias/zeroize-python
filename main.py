import zeroize
import numpy as np


arr = bytearray(b'1234567890')
arr_np = np.array([0] * 10, dtype=np.uint8)
arr_np[:] = arr
assert arr_np.tobytes() == b'1234567890'
zeroize.zeroize1(arr)
zeroize.zeroize_np(arr_np)
print("zeroize'ing...: ")
print("checking if is zeroized...")
assert arr == bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
assert all(arr_np == 0)
print("all good, bye!")