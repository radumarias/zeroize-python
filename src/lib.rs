use pyo3::prelude::*;
use pyo3::types::PyByteArray;
use zeroize_rs::Zeroize;

/// A Python module implemented in Rust.
#[pymodule]
fn zeroize(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(zeroize1, m)?)?;
    Ok(())
}


#[pyfunction]
fn zeroize1<'py>(arr: &Bound<'py, PyByteArray>) -> PyResult<()> {
    unsafe { arr.as_bytes_mut().zeroize(); }
    Ok(())
}
