import json
from pathlib import Path

import pytest

from runwayzero_agent.tools.sandbox import run_tests_in_sandbox


@pytest.mark.asyncio
async def test_run_tests_in_sandbox_reports_pass(tmp_path: Path):
    test_file = tmp_path / "test_passing.py"
    test_file.write_text("def test_truth():\n    assert 1 + 1 == 2\n")
    result = await run_tests_in_sandbox({
        "requirements": "",
        "test_path": str(test_file),
        "app_module_dir": "",
        "timeout_s": 60,
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["passed"] is True
    assert "1 passed" in payload["summary"]
    assert payload["duration_s"] >= 0


@pytest.mark.asyncio
async def test_run_tests_in_sandbox_reports_fail(tmp_path: Path):
    test_file = tmp_path / "test_failing.py"
    test_file.write_text("def test_lie():\n    assert 1 + 1 == 3\n")
    result = await run_tests_in_sandbox({
        "requirements": "",
        "test_path": str(test_file),
        "app_module_dir": "",
        "timeout_s": 60,
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["passed"] is False
    assert "1 failed" in payload["summary"] or "FAILED" in payload["stdout_tail"]


@pytest.mark.asyncio
async def test_run_tests_in_sandbox_uses_app_module_dir_for_pythonpath(tmp_path: Path):
    module_dir = tmp_path / "app_dir"
    module_dir.mkdir()
    (module_dir / "mymod.py").write_text("VALUE = 42\n")

    test_file = tmp_path / "test_import.py"
    test_file.write_text(
        "import mymod\n"
        "def test_imported_value():\n"
        "    assert mymod.VALUE == 42\n"
    )
    result = await run_tests_in_sandbox({
        "requirements": "",
        "test_path": str(test_file),
        "app_module_dir": str(module_dir),
        "timeout_s": 60,
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["passed"] is True, payload
