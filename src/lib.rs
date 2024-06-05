use std::any::Any;
use std::ops::Deref;

use libc::{self, size_t};
use numpy::{PyArray1, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes};
use zeroize_rs::Zeroize;

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

/// Calls the platform's underlying `mlock(2)` implementation.
unsafe fn _mlock(ptr: *mut u8, len: usize) -> bool {
    memsec::mlock(ptr, len)
}

/// Calls the platform's underlying `munlock(2)` implementation.
unsafe fn _munlock(ptr: *mut u8, len: usize) -> bool {
    memsec::munlock(ptr, len)
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
