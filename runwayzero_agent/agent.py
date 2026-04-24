"""RunwayZero agent — orchestrator using Anthropic tool-use API.

Entry points:
  run_pipeline(cve_id)       — async, programmatic
  lambda_handler(event, ctx) — AWS Lambda shim
  cli_main()                 — local CLI for the demo
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import anthropic

from runwayzero_agent import config
from runwayzero_agent import tools as _tools_module  # noqa: F401 — triggers register_tool()
from runwayzero_agent.tool_registry import dispatch_tool, get_tool_definitions

MODEL = "claude-opus-4-7"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"


def _build_user_prompt(cve_id: str, cfg) -> str:
    test_path = os.environ.get("RUNWAYZERO_TEST_PATH", "tests/test_ssrf.py")
    return (
        f"A new vulnerability was reported: {cve_id}. "
        f"Investigate impact in our infrastructure and remediate end-to-end.\n\n"
        f"Runtime values you need:\n"
        f"  instance_id    = {cfg.target_instance_id}\n"
        f"  host           = {cfg.target_host}\n"
        f"  role_name      = {cfg.target_role_name}  (use this in the IMDS exploit URL path)\n"
        f"  app_module_dir = {cfg.app_module_dir}    (pass to run_tests_in_sandbox)\n"
        f"  test_path      = {test_path}             (pass to run_tests_in_sandbox)\n"
    )


def _extract_tool_result_text(result: dict[str, Any]) -> str:
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError):
        return json.dumps(result)


async def run_pipeline(cve_id: str) -> dict[str, Any]:
    cfg = config.load()
    system_prompt = SYSTEM_PROMPT_PATH.read_text()
    user_prompt = _build_user_prompt(cve_id, cfg)
    tools = get_tool_definitions()

    client = anthropic.AsyncAnthropic()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_prompt}]

    while True:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=8096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        # Collect any text blocks for display
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text = block.text.strip()
                if text:
                    print(f"[AGENT] {text[:500]}", flush=True)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason != "tool_use":
            print(f"[WARN] unexpected stop_reason: {response.stop_reason}", flush=True)
            break

        # Append assistant message with all content blocks
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool call and collect results
        tool_results = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            print(f"[TOOL] {block.name}({json.dumps(block.input, default=str)[:200]})", flush=True)
            result = await dispatch_tool(block.name, block.input)
            result_text = _extract_tool_result_text(result)
            is_error = result.get("is_error", False)
            print(f"[RESULT] {result_text[:300]}", flush=True)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_text,
                **({"is_error": True} if is_error else {}),
            })

        messages.append({"role": "user", "content": tool_results})

    return {"cve_id": cve_id, "status": "completed"}


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    cve_id = event.get("cve_id", "CVE-2026-33626")
    return asyncio.run(run_pipeline(cve_id))


def cli_main() -> None:
    cve_id = sys.argv[1] if len(sys.argv) > 1 else "CVE-2026-33626"
    result = asyncio.run(run_pipeline(cve_id))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    cli_main()
