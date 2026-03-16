"""Test log parser Python fallback."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src/bridge"))
from server import _python_parse

def test_detects_errors():
    logs = "2026-01-01 10:00:00 INFO Starting\n2026-01-01 10:00:01 ERROR Connection refused\n"
    result = _python_parse(logs)
    assert len(result["errors"]) == 1
    assert result["probable_cause"] == "Service connectivity failure."

def test_detects_oom():
    logs = "java.lang.OutOfMemoryError: Java heap space"
    result = _python_parse(logs)
    assert "Memory exhaustion" in result["probable_cause"]

def test_detects_timeout():
    logs = "ERROR: upstream timeout after 30s"
    result = _python_parse(logs)
    assert "Timeout cascade" in result["probable_cause"]

def test_generic_error():
    logs = "ERROR: something went wrong"
    result = _python_parse(logs)
    assert "Application error" in result["probable_cause"]

def test_api_root():
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "logs-service"

def test_api_health():
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_analyze():
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)
    response = client.post("/analyze", json={"raw_logs": "ERROR: fail", "session_id": "test"})
    assert response.status_code == 200
    assert len(response.json()["errors"]) == 1

def test_no_errors_with_warnings():
    logs = "WARN: something is slow"
    result = _python_parse(logs)
    assert len(result["errors"]) == 0
    assert len(result["warnings"]) == 1
    assert result["probable_cause"] == "No errors detected."

def test_no_errors():
    logs = "2026-01-01 INFO All good\n"
    result = _python_parse(logs)
    assert result["errors"] == []
    assert "No errors" in result["probable_cause"]

def test_analyze_rust_mock():
    import server
    from fastapi.testclient import TestClient
    from unittest.mock import MagicMock
    import json
    
    server.USE_RUST = True
    mock_log_parser = MagicMock()
    mock_log_parser.parse_logs_py.return_value = json.dumps({
        "errors": [{"message": "rust error"}],
        "warnings": [{"message": "rust warn"}],
        "anomalies": [],
        "probable_cause": "rust cause",
        "total_lines": 1,
        "error_rate": 1.0
    })
    server.log_parser = mock_log_parser # Set it on the module
    
    client = TestClient(server.app)
    response = client.post("/analyze", json={"raw_logs": "test", "session_id": "s1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "rust error" in data["errors"]
    assert data["probable_cause"] == "rust cause"
    
    # Restore
    server.USE_RUST = False
    if hasattr(server, 'log_parser'):
        del server.log_parser

def test_module_import_rust_success():
    import sys
    from unittest.mock import MagicMock
    import importlib
    
    mock_log_parser = MagicMock()
    sys.modules["log_parser"] = mock_log_parser
    
    import src.bridge.server as server
    importlib.reload(server)
    
    assert server.USE_RUST is True
    
    # Cleanup
    del sys.modules["log_parser"]
    importlib.reload(server)
