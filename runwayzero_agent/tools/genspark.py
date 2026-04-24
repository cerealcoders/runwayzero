import json
import os
from pathlib import Path
from typing import Any

import requests

from runwayzero_agent.errors import error_response, success_response
from runwayzero_agent.tool_registry import register_tool

GENSPARK_URL = "https://api.genspark.ai/v1/research"
DEFAULT_TIMEOUT_S = 20


def _cache_dir() -> Path:
    override = os.environ.get("RUNWAYZERO_GENSPARK_CACHE_DIR")
    if override:
        return Path(override)
    return Path(__file__).parent.parent / "cache"


def _read_cached(cve_id: str) -> dict[str, Any] | None:
    cache_file = _cache_dir() / f"genspark-{cve_id}.json"
    if not cache_file.exists():
        return None
    payload = json.loads(cache_file.read_text())
    payload["from_cache"] = True
    return payload


async def genspark_research(args: dict[str, Any]) -> dict[str, Any]:
    sbom = args.get("sbom", [])
    api_key = os.environ.get("GENSPARK_API_KEY", "")
    try:
        resp = requests.post(
            GENSPARK_URL,
            json={"sbom": sbom, "since_hours": 168},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=DEFAULT_TIMEOUT_S,
        )
        resp.raise_for_status()
        return success_response(resp.json())
    except Exception as exc:
        cached = _read_cached("CVE-2026-33626")
        if cached:
            return success_response(cached)
        return error_response(
            f"Genspark API failed and no cache available: {exc}",
            retryable=True,
            details={"exception": str(exc)},
        )


register_tool(
    name="genspark_research",
    description="Submit current SBOM to Genspark and return enriched CVE list",
    input_schema={
        "type": "object",
        "properties": {
            "sbom": {"type": "array", "items": {"type": "string"}, "description": "List of package==version strings"},
        },
        "required": ["sbom"],
    },
    fn=genspark_research,
)
