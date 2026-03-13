//! PyO3 Python extension — exposes Rust parser to Python.
pub mod parser;

#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pyfunction]
fn parse_logs_py(raw: &str) -> PyResult<String> {
    let result = parser::parse_logs(raw);
    Ok(serde_json::to_string(&result).unwrap())
}

#[cfg(feature = "python")]
#[pymodule]
fn log_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_logs_py, m)?)?;
    Ok(())
}
