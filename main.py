import zeroize

arr = bytearray(b'1234567890')
zeroize.zeroize1(arr)
assert arr == bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
print("all good, bye!")