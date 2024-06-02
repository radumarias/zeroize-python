use numpy::{PyArray1, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::types::PyByteArray;
use zeroize_rs::Zeroize;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    m.add_function(wrap_pyfunction!(zeroize_np, m)?)?;
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
