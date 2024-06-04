use std::mem;
use std::sync::Once;

use libc::{self, size_t};
use libsodium_sys::{
    sodium_init
    , sodium_mlock
    , sodium_munlock,
};
use numpy::{PyArray1, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyCFunction};
use zeroize_rs::Zeroize;

/// The global [`sync::Once`] that ensures we only perform
/// library initialization one time.
static INIT: Once = Once::new();

/// A flag that returns whether this library has been safely
/// initialized.
static mut INITIALIZED: bool = false;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize<'py>(_py: Python, m: &Bound<'py, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    m.add_function(wrap_pyfunction!(zeroize_np, m)?)?;
    // m.add_function(wrap_pyfunction!(zeroize_mv, m)?)?;
    m.add_function(wrap_pyfunction!(mlock, m)?)?;
    m.add_function(wrap_pyfunction!(munlock, m)?)?;
    m.add_function(wrap_pyfunction!(mlock_np, m)?)?;
    m.add_function(wrap_pyfunction!(munlock_np, m)?)?;
    Ok(())
}


#[pyfunction]
fn zeroize1<'py>(arr: &Bound<'py, PyByteArray>) -> PyResult<()> {
    unsafe { arr.as_bytes_mut().zeroize(); }
    Ok(())
}

#[pyfunction]
fn zeroize_np<'py>(arr: &Bound<'py, PyArray1<u8>>) -> PyResult<()> {
    unsafe { arr.as_slice_mut().unwrap().zeroize(); }
    Ok(())
}

#[pyfunction]
fn mlock<'py>(arr: &Bound<'py, PyByteArray>) -> PyResult<()> {
    unsafe {
        if !init() {
            panic!("libsodium failed to initialize")
        }
        if !_mlock(arr.as_bytes_mut().as_mut_ptr()) {
            panic!("mlock failed")
        }
    }
    Ok(())
}

#[pyfunction]
fn mlock_np<'py>(arr: &Bound<'py, PyArray1<u8>>) -> PyResult<()> {
    unsafe {
        if !init() {
            panic!("libsodium failed to initialize")
        }
        if !_mlock(arr.as_slice_mut().unwrap().as_mut_ptr()) {
            panic!("mlock failed")
        }
    }
    Ok(())
}

#[pyfunction]
fn munlock<'py>(arr: &Bound<'py, PyByteArray>) -> PyResult<()> {
    unsafe {
        if !init() {
            panic!("libsodium failed to initialize")
        }
        if !_munlock(arr.as_bytes_mut().as_mut_ptr()) {
            panic!("mlock failed")
        }
    }
    Ok(())
}

#[pyfunction]
fn munlock_np<'py>(arr: &Bound<'py, PyArray1<u8>>) -> PyResult<()> {
    unsafe {
        if !init() {
            panic!("libsodium failed to initialize")
        }
        if !_munlock(arr.as_slice_mut().unwrap().as_mut_ptr()) {
            panic!("mlock failed")
        }
    }
    Ok(())
}

// #[pyfunction]
// fn zeroize_mv<'py>(arr: &PyMemoryView, len: usize) -> PyResult<()> {
//     // Get the buffer information
//     let buffer = PyBuffer::<u8>::get(arr)?;
//
//     // Get the raw mutable pointer and length of the memory view
//     let ptr = arr.as_ptr() as *mut u8;
//
//     // Create a mutable slice from the raw pointer and length
//     let arr: &mut [u8] = unsafe { std::slice::from_raw_parts_mut(ptr, len) };
//
//     arr.zeroize();
//
//     Ok(())
// }

/// Initialized libsodium. This function *must* be called at least once
/// prior to using any of the other functions in this library, and
/// callers *must* verify that it returns `true`. If it returns `false`,
/// libsodium was unable to be properly set up and this library *must
/// not* be used.
///
/// Calling it multiple times is a no-op.
pub(crate) fn init() -> bool {
    unsafe {
        INIT.call_once(|| {
            // NOTE: Calls to transmute fail to compile if the source
            // and destination type have a different size. We (ab)use
            // this fact to statically assert the size of types at
            // compile-time.
            //
            // We assume that we can freely cast between rust array
            // sizes and [`libc::size_t`]. If that's not true, DO NOT
            // COMPILE.
            #[allow(clippy::useless_transmute)]
                let _ = std::mem::transmute::<usize, size_t>(0);

            let mut failure = false;

            // sodium_init returns 0 on success, -1 on failure, and 1 if
            // the library is already initialized; someone else might
            // have already initialized it before us, so we only care
            // about failure
            failure |= sodium_init() == -1;

            INITIALIZED = !failure;
        });

        INITIALIZED
    }
}

/// Calls the platform's underlying `mlock(2)` implementation.
unsafe fn _mlock<T>(ptr: *mut T) -> bool {
    sodium_mlock(ptr.cast(), mem::size_of::<T>()) == 0
}

/// Calls the platform's underlying `munlock(2)` implementation.
unsafe fn _munlock<T>(ptr: *mut T) -> bool {
    sodium_munlock(ptr.cast(), mem::size_of::<T>()) == 0
}

#[cfg(test)]
mod test {
    use zeroize_rs::Zeroize;

    #[test]
    fn test_zeroize() {
        let mut arr = [1, 2, 3, 4, 5];
        arr.zeroize();
        assert_eq!(arr, [0, 0, 0, 0, 0]);
    }
}
