import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from runwayzero_agent import agent


@pytest.mark.asyncio
async def test_run_pipeline_calls_anthropic_and_returns_result():
    """run_pipeline must build options, call the Anthropic API, handle tool calls,
    and return a dict with cve_id and status."""
    fake_tool_use = MagicMock()
    fake_tool_use.type = "tool_use"
    fake_tool_use.id = "tu_1"
    fake_tool_use.name = "genspark_research"
    fake_tool_use.input = {"sbom": ["lmdeploy==0.12.2"]}

    # First response: tool call. Second response: end_turn.
    resp1 = MagicMock()
    resp1.stop_reason = "tool_use"
    resp1.content = [fake_tool_use]

    resp2 = MagicMock()
    resp2.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "CVE-2026-33626 remediated successfully."
    resp2.content = [text_block]

    fake_tool_result = {"content": [{"type": "text", "text": json.dumps({"cves": []})}]}

    with patch("runwayzero_agent.agent.anthropic.AsyncAnthropic") as mock_cls, \
         patch("runwayzero_agent.agent.dispatch_tool", new=AsyncMock(return_value=fake_tool_result)):
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create = AsyncMock(side_effect=[resp1, resp2])

        result = await agent.run_pipeline("CVE-2026-33626")

    assert result["cve_id"] == "CVE-2026-33626"
    assert result["status"] == "completed"


def test_lambda_handler_runs_pipeline():
    with patch("runwayzero_agent.agent.asyncio") as mock_asyncio:
        mock_asyncio.run.return_value = {"cve_id": "CVE-2026-33626", "status": "completed"}
        result = agent.lambda_handler({"cve_id": "CVE-2026-33626"}, None)
    assert result["status"] == "completed"
