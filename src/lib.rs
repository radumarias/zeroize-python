use numpy::{PyArray1, PyArrayMethods};
use pyo3::buffer::PyBuffer;
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyMemoryView};
use zeroize_rs::Zeroize;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    m.add_function(wrap_pyfunction!(zeroize_np, m)?)?;
    // m.add_function(wrap_pyfunction!(zeroize_mv, m)?)?;
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
