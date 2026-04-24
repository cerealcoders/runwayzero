"""Sandbox test runner — executes pytest against patched dependencies."""

import subprocess
import time


def run_tests_in_sandbox(requirements: str, test_path: str, timeout_s: int = 120) -> dict:
    """Install requirements and run pytest in an isolated subprocess.

    Returns:
        {passed: bool, summary, stdout_tail, stderr_tail, duration_s}
    """
    # TODO: Implement — create temp venv, pip install, run pytest
    return {"error": "Not implemented", "retryable": False, "details": {}}
