use std::any::Any;
use std::mem;
use std::ops::Deref;
use std::sync::Once;

use libc::{self, size_t};
use libsodium_sys::{
    sodium_init
    , sodium_mlock
    , sodium_munlock,
};
use numpy::{PyArray1, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes};
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
    // m.add_function(wrap_pyfunction!(zeroize_mv, m)?)?;
    m.add_function(wrap_pyfunction!(mlock, m)?)?;
    m.add_function(wrap_pyfunction!(munlock, m)?)?;
    Ok(())
}


#[pyfunction]
fn zeroize1<'py>(arr: &Bound<'py, PyAny>) -> PyResult<()> {
    as_array_mut(arr)?.zeroize();
    Ok(())
}

#[pyfunction]
fn mlock<'py>(arr: &Bound<'py, PyAny>) -> PyResult<()> {
    if !init() {
        return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "libsodium failed to initialize",
        ));
    }
    unsafe {
        let arr = as_array_mut(arr)?;
        if !_mlock(arr.as_mut_ptr(), arr.len()) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "mlock failed",
            ));
        }
    }
    Ok(())
}

#[pyfunction]
fn munlock<'py>(arr: &Bound<'py, PyAny>) -> PyResult<()> {
    if !init() {
        return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "libsodium failed to initialize",
        ));
    }
    unsafe {
        let arr = as_array_mut(arr)?;
        if !_munlock(arr.as_mut_ptr(), arr.len()) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "mlock failed",
            ));
        }
    }
    Ok(())
}

fn as_array_mut<'a>(arr: &'a Bound<PyAny>) -> PyResult<&'a mut [u8]> {
    let arr = unsafe {
        if let Ok(arr) = arr.downcast::<PyByteArray>() {
            arr.as_bytes_mut()
        } else if let Ok(arr) = arr.downcast::<PyArray1<u8>>() {
            arr.as_slice_mut().unwrap()
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Expected a PyByteArray or PyArray1<u8>",
            ));
        }
    };
    Ok(arr)
}

fn as_array<'a>(arr: &'a Bound<PyAny>) -> PyResult<&'a [u8]> {
    let arr = unsafe {
        if let Ok(arr) = arr.downcast::<PyByteArray>() {
            arr.as_bytes()
        } else if let Ok(arr) = arr.downcast::<PyBytes>() {
            arr.as_bytes()
        } else if let Ok(arr) = arr.downcast::<PyArray1<u8>>() {
            arr.as_slice().unwrap()
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Expected a PyByteArray or PyArray1<u8>",
            ));
        }
    };
    Ok(arr)
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
fn init() -> bool {
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
unsafe fn _mlock<T>(ptr: *mut T, len: usize) -> bool {
    sodium_mlock(ptr.cast(), len) == 0
}

/// Calls the platform's underlying `munlock(2)` implementation.
unsafe fn _munlock<T>(ptr: *mut T, len: usize) -> bool {
    sodium_munlock(ptr.cast(), len) == 0
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
