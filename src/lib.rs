#![deny(warnings)]
use numpy::{PyArray1, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes};
use zeroize_rs::Zeroize;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    // m.add_function(wrap_pyfunction!(zeroize_mv, m)?)?;
    m.add_function(wrap_pyfunction!(mlock, m)?)?;
    m.add_function(wrap_pyfunction!(munlock, m)?)?;
    Ok(())
}

#[pyfunction]
fn zeroize1(arr: &Bound<'_, PyAny>) -> PyResult<()> {
    as_array_mut(arr)?.zeroize();
    Ok(())
}

#[pyfunction]
fn mlock(arr: &Bound<'_, PyAny>) -> PyResult<()> {
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
fn munlock(arr: &Bound<'_, PyAny>) -> PyResult<()> {
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
                "Expected a bytearray or numpy.array",
            ));
        }
    };
    Ok(arr)
}

#[allow(dead_code)]
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
                "Expected a bytearray, bytes or numpy.array",
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
    use super::{_mlock, _munlock};
    use zeroize_rs::Zeroize;

    #[test]
    fn test_zeroize() {
        let mut arr = [1, 2, 3, 4, 5];
        arr.zeroize();
        assert_eq!(arr, [0, 0, 0, 0, 0]);
    }

    #[test]
    fn test_mlock() {
        let mut arr = [1, 2, 3, 4, 5];
        let mut arr2 = vec![0; 4096];
        let mut arr3 = vec![0; 4096 * 4096];
        unsafe {
            let ptr = arr.as_mut_ptr();
            let len = arr.len();
            _mlock(ptr, len);
            _munlock(ptr, len);

            let ptr = arr2.as_mut_ptr();
            let len = arr2.len();
            _mlock(ptr, len);
            _munlock(ptr, len);

            let ptr = arr3.as_mut_ptr();
            let len = arr3.len();
            _mlock(ptr, len);
            _munlock(ptr, len);
        }
    }
}
