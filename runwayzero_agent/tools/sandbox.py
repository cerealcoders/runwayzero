import os
import shutil
import subprocess
import sys
import tempfile
import time
import venv
from pathlib import Path
from typing import Any

from runwayzero_agent.errors import error_response, success_response
from runwayzero_agent.tool_registry import register_tool


async def run_tests_in_sandbox(args: dict[str, Any]) -> dict[str, Any]:
    requirements = args.get("requirements", "")
    test_path = args["test_path"]
    app_module_dir = args.get("app_module_dir", "")
    timeout_s = int(args.get("timeout_s", 180))
    start = time.monotonic()
    sandbox = Path(tempfile.mkdtemp(prefix="runwayzero-sandbox-"))
    try:
        venv.create(sandbox / "venv", with_pip=True)
        py = sandbox / "venv" / "bin" / "python"
        if requirements.strip():
            req_file = sandbox / "requirements.txt"
            req_file.write_text(requirements)
            install = subprocess.run(
                [str(py), "-m", "pip", "install", "-q", "-r", str(req_file)],
                capture_output=True, text=True, timeout=timeout_s,
            )
            if install.returncode != 0:
                return error_response(
                    "pip install in sandbox failed",
                    retryable=False,
                    details={"stderr": install.stderr[-1000:]},
                )
        subprocess.run(
            [str(py), "-m", "pip", "install", "-q", "pytest", "httpx"],
            capture_output=True, text=True, timeout=120, check=True,
        )
        env = {**os.environ}
        if app_module_dir:
            existing_pp = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                f"{app_module_dir}:{existing_pp}" if existing_pp else app_module_dir
            )
        proc = subprocess.run(
            [str(py), "-m", "pytest", "-v", test_path],
            capture_output=True, text=True, timeout=timeout_s, env=env,
        )
        duration = round(time.monotonic() - start, 2)
        passed = proc.returncode == 0
        summary = next(
            (ln for ln in reversed(proc.stdout.splitlines()) if " passed" in ln or " failed" in ln),
            "no summary",
        )
        return success_response({
            "passed": passed,
            "summary": summary.strip(),
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-500:],
            "duration_s": duration,
        })
    except subprocess.TimeoutExpired as exc:
        return error_response(
            f"Sandbox test execution timed out after {timeout_s}s",
            retryable=False, details={"stderr": str(exc)},
        )
    except Exception as exc:
        return error_response(f"Sandbox failure: {exc}", retryable=False)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


register_tool(
    name="run_tests_in_sandbox",
    description=(
        "Create an ephemeral venv, install the FULL patched requirements (not just one line), "
        "set PYTHONPATH to include app_module_dir (so `from app import app` works), and run pytest "
        "at test_path. Returns pass/fail + summary."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "requirements": {"type": "string", "description": "Full requirements.txt content to install"},
            "test_path": {"type": "string", "description": "Absolute path to the pytest test file"},
            "app_module_dir": {"type": "string", "description": "Directory added to PYTHONPATH (for app.py import)"},
            "timeout_s": {"type": "integer", "default": 180},
        },
        "required": ["requirements", "test_path"],
    },
    fn=run_tests_in_sandbox,
)
