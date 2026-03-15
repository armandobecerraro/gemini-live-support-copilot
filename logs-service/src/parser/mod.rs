//! Core log parsing engine.
//! Target: > 500 MB/s throughput, < 50ms P99 latency.
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

static ERROR_RE: OnceLock<Regex> = OnceLock::new();
static WARN_RE: OnceLock<Regex>  = OnceLock::new();
static TS_RE:   OnceLock<Regex>  = OnceLock::new();

fn error_re() -> &'static Regex {
    ERROR_RE.get_or_init(|| Regex::new(r"(?i)(ERROR|FATAL|EXCEPTION|CRITICAL|PANIC)").unwrap())
}
fn warn_re() -> &'static Regex {
    WARN_RE.get_or_init(|| Regex::new(r"(?i)(WARN|WARNING)").unwrap())
}
fn ts_re() -> &'static Regex {
    TS_RE.get_or_init(|| {
        Regex::new(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})|(\d{2}:\d{2}:\d{2}.\d{3})").unwrap()
    })
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ParsedLogEntry {
    pub line_number: usize,
    pub level: String,
    pub message:   String,
    pub timestamp: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LogAnalysisResult {
    pub errors:          Vec<ParsedLogEntry>,
    pub warnings:        Vec<ParsedLogEntry>,
    pub anomalies:       Vec<String>,
    pub probable_cause:  String,
    pub timestamp_range: Option<String>,
    pub total_lines:     usize,
    pub error_rate:      f64,
}

pub fn parse_logs(raw: &str) -> LogAnalysisResult {
    let lines: Vec<&str> = raw.lines().collect();
    let total = lines.len();

    let (errors, warnings): (Vec<_>, Vec<_>) = lines
        .iter()
        .enumerate()
        .filter_map(|(i, line)| {
            let level = if error_re().is_match(line) {
                Some("ERROR")
            } else if warn_re().is_match(line) {
                Some("WARN")
            } else {
                None
            };
            level.map(|l| {
                let ts = ts_re().find(line).map(|m| m.as_str().to_string());
                ParsedLogEntry {
                    line_number: i + 1,
                    level: l.to_string(),
                    message: line.chars().take(300).collect(),
                    timestamp: ts,
                }
            })
        })
        .partition(|e| e.level == "ERROR");

    let timestamps: Vec<&str> = lines
        .iter()
        .filter_map(|l| ts_re().find(l).map(|m| m.as_str()))
        .collect();

    let ts_range = if timestamps.len() >= 2 {
        Some(format!("{} → {}", timestamps[0], timestamps[timestamps.len() - 1]))
    } else {
        None
    };

    let error_rate = if total > 0 { errors.len() as f64 / total as f64 } else { 0.0 };

    let probable_cause = infer_cause(&errors);

    LogAnalysisResult {
        errors: errors.into_iter().take(50).collect(),
        warnings: warnings.into_iter().take(30).collect(),
        anomalies: vec![],
        probable_cause,
        timestamp_range: ts_range,
        total_lines: total,
        error_rate,
    }
}

fn infer_cause(errors: &[ParsedLogEntry]) -> String {
    if errors.is_empty() {
        return "No errors detected.".into();
    }
    let sample = errors.iter().take(5).map(|e| e.message.as_str()).collect::<Vec<_>>().join(" ");
    if sample.contains("Connection refused") || sample.contains("ECONNREFUSED") {
        "Service connectivity failure — downstream service unreachable.".into()
    } else if sample.contains("OutOfMemory") || sample.contains("OOM") {
        "Memory exhaustion — OOM condition detected.".into()
    } else if sample.contains("timeout") || sample.contains("Timeout") {
        "Timeout cascade — upstream latency or resource contention.".into()
    } else if sample.contains("NullPointer") || sample.contains("NullRef") {
        "Null reference exception — unhandled null in application code.".into()
    } else if sample.contains("disk") || sample.contains("No space left") {
        "Disk space exhaustion — storage full.".into()
    } else {
        format!("Application error detected in {} log lines.", errors.len())
    }
}
