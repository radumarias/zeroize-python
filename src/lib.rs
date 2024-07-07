#![deny(warnings)]
#![doc(html_playground_url = "https://play.rust-lang.org")]
#![deny(clippy::all)]
#![deny(clippy::correctness)]
#![deny(clippy::suspicious)]
#![deny(clippy::complexity)]
#![deny(clippy::perf)]
#![deny(clippy::style)]
#![deny(clippy::pedantic)]
#![deny(clippy::nursery)]
#![deny(clippy::cargo)]
// #![deny(missing_docs)]
#![allow(clippy::similar_names)]
#![allow(clippy::too_many_arguments)]
#![allow(clippy::significant_drop_tightening)]
#![allow(clippy::redundant_closure)]
#![allow(clippy::missing_errors_doc)]
#![allow(clippy::redundant_pub_crate)]

use numpy::{PyArray1, PyArrayMethods};
use pyo3::buffer::PyBuffer;
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes};
use zeroize_rs::Zeroize;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    m.add_function(wrap_pyfunction!(mlock, m)?)?;
    m.add_function(wrap_pyfunction!(munlock, m)?)?;
    Ok(())
}

#[pyfunction]
fn zeroize1(arr: &Bound<'_, PyAny>, py: Python<'_>) -> PyResult<()> {
    as_array_mut(arr, py)?.zeroize();
    Ok(())
}

#[pyfunction]
fn mlock(arr: &Bound<'_, PyAny>, py: Python<'_>) -> PyResult<()> {
    let arr = as_array_mut(arr, py)?;
    unsafe {
        if !_mlock(arr.as_mut_ptr(), arr.len()) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "mlock failed",
            ));
        }
    }
    Ok(())
}

#[pyfunction]
fn munlock(arr: &Bound<'_, PyAny>, py: Python<'_>) -> PyResult<()> {
    let arr = as_array_mut(arr, py)?;
    unsafe {
        if !_munlock(arr.as_mut_ptr(), arr.len()) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "munlock failed",
            ));
        }
    }
    Ok(())
}

fn as_array_mut<'a>(arr: &'a Bound<PyAny>, py: Python<'a>) -> PyResult<&'a mut [u8]> {
    let arr = {
        if let Ok(arr) = arr.downcast::<PyByteArray>() {
            unsafe { arr.as_bytes_mut() }
        } else if let Ok(arr) = arr.downcast::<PyArray1<u8>>() {
            unsafe { arr.as_slice_mut().unwrap() }
        } else {
            let buffer: PyBuffer<u8> = PyBuffer::get_bound(arr).map_err(|err| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "expected a bytearray, bytes, array.array or numpy.array: {err}"
                ))
            })?;
            let ptr = buffer.buf_ptr().cast::<u8>();
            let len = buffer
                .as_slice(py)
                .ok_or_else(|| {
                    PyErr::new::<pyo3::exceptions::PyTypeError, _>("extracting len failed")
                })?
                .len();
            let data_slice = unsafe { std::slice::from_raw_parts_mut(ptr, len) };
            data_slice
        }
    };
    Ok(arr)
}

#[allow(dead_code)]
fn as_array<'a>(arr: &'a Bound<PyAny>, py: Python<'a>) -> PyResult<&'a [u8]> {
    let arr = {
        if let Ok(arr) = arr.downcast::<PyByteArray>() {
            unsafe { arr.as_bytes() }
        } else if let Ok(arr) = arr.downcast::<PyBytes>() {
            arr.as_bytes()
        } else if let Ok(arr) = arr.downcast::<PyArray1<u8>>() {
            unsafe { arr.as_slice().unwrap() }
        } else {
            let buffer: PyBuffer<u8> = PyBuffer::get_bound(arr).map_err(|err| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "expected a bytearray, bytes, array.array or numpy.array: {err}"
                ))
            })?;
            let ptr = buffer.buf_ptr() as *const u8;
            let len = buffer
                .as_slice(py)
                .ok_or_else(|| {
                    PyErr::new::<pyo3::exceptions::PyTypeError, _>("extracting len failed")
                })?
                .len();
            let data_slice = unsafe { std::slice::from_raw_parts(ptr, len) };
            data_slice
        }
    };
    Ok(arr)
}

/// Calls the platform's underlying `mlock(2)` implementation.
unsafe fn _mlock(ptr: *mut u8, len: usize) -> bool {
    memsec::mlock(ptr, len)
}

/// Calls the platform's underlying `munlock(2)` implementation.
unsafe fn _munlock(ptr: *mut u8, len: usize) -> bool {
    let r = memsec::munlock(ptr, len);
    if !r && cfg!(target_os = "windows") {
        // On windows if we munlock 2 times on the same page we get an error.
        // This can happen if we munlock 2 vars that are in the same page.
        return true;
    }
    r
}

#[cfg(test)]
mod test {
    use super::{_mlock, _munlock};
    use zeroize_rs::Zeroize;

    #[test]
    fn test_zeroize() {
        let mut arr = [1, 2, 3, 4, 5];
        arr.zeroize();
        assert_eq!(arr, [0, 0, 0, 0, 0]);
    }

    #[test]
    #[allow(clippy::cast_possible_truncation)]
    #[allow(clippy::cast_sign_loss)]
    fn test_mlock() {
        let sizes_mb = [0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 4.42];
        for size in sizes_mb {
            println!("Check for size {size} MB");
            let mut arr = vec![0; (size * 1024.0 * 1024.0) as usize];
            let ptr = arr.as_mut_ptr();
            let len = arr.len();
            unsafe {
                _mlock(ptr, len);
                _munlock(ptr, len);
            }
        }
    }
}
