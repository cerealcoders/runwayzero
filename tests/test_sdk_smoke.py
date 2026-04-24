"""Validate the anthropic SDK surface and tool-calling patterns we depend on.
No network calls — imports and structural checks only."""

import asyncio
import json

import pytest


def test_anthropic_async_client_imports():
    """Core SDK classes must import cleanly."""
    from anthropic import AsyncAnthropic  # noqa: F401
    from anthropic.types import Message, TextBlock, ToolUseBlock  # noqa: F401


def test_anthropic_tool_definition_format():
    """Validate the tool definition dict shape that we pass to messages.create()."""
    tool_def = {
        "name": "ssm_inventory_scan",
        "description": "Find managed EC2 instances reporting a given package",
        "input_schema": {
            "type": "object",
            "properties": {
                "package": {"type": "string", "description": "pip package name"},
            },
            "required": ["package"],
        },
    }
    assert tool_def["name"]
    assert "input_schema" in tool_def
    assert tool_def["input_schema"]["type"] == "object"


@pytest.mark.asyncio
async def test_async_tool_function_pattern():
    """Our tools are async functions that take a dict and return a dict.
    Validate this pattern works before building all 11 tools."""
    async def example_tool(args: dict) -> dict:
        return {"content": [{"type": "text", "text": json.dumps({"result": args.get("x")})}]}

    result = await example_tool({"x": "hello"})
    assert "content" in result
    payload = json.loads(result["content"][0]["text"])
    assert payload["result"] == "hello"


def test_tool_registry_pattern():
    """Validate the tool registry pattern: a dict mapping tool names to callables."""
    async def noop(args: dict) -> dict:
        return {"content": [{"type": "text", "text": "{}"}]}

    registry = {"noop": noop}
    assert "noop" in registry
    assert callable(registry["noop"])
