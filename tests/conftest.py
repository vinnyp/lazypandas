"""Test isolation: clean accumulated CSV artifacts before each test.

After B6's ambiguity check, the legacy tests that share tests/file_output/
fail on re-runs when multiple matching files accumulate. This autouse
fixture clears the directory between tests so the suite is resilient to
stale state. Obsoleted by chunk-tests T4 (move legacy tests to tmp_path).
"""
from pathlib import Path

import pytest

_FILE_OUTPUT = Path(__file__).parent / "file_output"


@pytest.fixture(autouse=True, scope="session")
def _clean_file_output_at_session_start():
    """Clear stale CSVs once per session. Tests within a session may
    intentionally accumulate state (e.g. test_trace_exported)."""
    if _FILE_OUTPUT.is_dir():
        for csv in _FILE_OUTPUT.glob("*.csv"):
            csv.unlink()
    yield
