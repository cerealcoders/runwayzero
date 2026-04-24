import time
from typing import Any

import requests

from runwayzero_agent.errors import error_response, success_response
from runwayzero_agent.tool_registry import register_tool


async def verify_service_healthy(args: dict[str, Any]) -> dict[str, Any]:
    url = args["url"]
    timeout = int(args.get("timeout_s", 5))
    start = time.monotonic()
    try:
        resp = requests.get(url, timeout=timeout)
        return success_response({
            "healthy": 200 <= resp.status_code < 300,
            "status_code": resp.status_code,
            "response_ms": int((time.monotonic() - start) * 1000),
        })
    except Exception as exc:
        return error_response(f"health check failed: {exc}", retryable=True)


async def verify_exploit_blocked(args: dict[str, Any]) -> dict[str, Any]:
    try:
        resp = requests.post(args["url"], json=args["payload"], timeout=10)
        body = resp.text[:1000]
        is_2xx = 200 <= resp.status_code < 300
        contains_creds = any(
            marker in body
            for marker in ["AccessKeyId", "SecretAccessKey", "SessionToken"]
        )
        blocked = not is_2xx
        if not blocked and contains_creds:
            note = "exploit succeeded — IAM credential markers in response body"
        elif not blocked:
            note = "inconclusive — 2xx response without obvious markers; treating as not-blocked per strict contract"
        else:
            note = f"blocked — server rejected with status {resp.status_code}"
        return success_response({
            "blocked": blocked,
            "status_code": resp.status_code,
            "response_body_preview": body[:500],
            "note": note,
        })
    except Exception as exc:
        return error_response(f"exploit verification failed: {exc}", retryable=True)


register_tool(
    name="verify_service_healthy",
    description="GET the service health endpoint and return whether it returned 2xx",
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "timeout_s": {"type": "integer", "default": 5},
        },
        "required": ["url"],
    },
    fn=verify_service_healthy,
)

register_tool(
    name="verify_exploit_blocked",
    description=(
        "POST the SSRF payload to the chat endpoint. Strict contract: blocked = True only "
        "when the server returned an explicit 4xx/5xx. A 2xx response is treated as "
        "inconclusive/not-blocked even without obvious credential markers."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "payload": {"type": "object", "description": "JSON body to POST (e.g. {image_url: ...})"},
        },
        "required": ["url", "payload"],
    },
    fn=verify_exploit_blocked,
)
