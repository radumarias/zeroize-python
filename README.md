# Zeroize

Securely clear secrets from memory built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.
Uses a portable pure Rust implementation that works everywhere.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood.

# Exmple

```python
import zeroize

arr = bytearray(b'1234567890')
zeroize.zeroize1(arr)
assert arr == bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
```
