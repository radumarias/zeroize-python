# Zerioze

Securely clear secrets from memory built on stable Rust primitives which guarantee memory is zeroed using an operation will not be 'optimized away' by the compiler.
Uses a portable pure Rust implementation that works everywhere.

It uses [zeroize](https://crates.io/crates/zeroize) crate under the hood.