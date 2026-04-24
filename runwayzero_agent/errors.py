import json
from typing import Any


def success_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, default=str)}]}


def error_response(
    message: str, *, retryable: bool = False, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    body = {"error": message, "retryable": retryable, "details": details or {}}
    return {
        "content": [{"type": "text", "text": json.dumps(body, default=str)}],
        "is_error": True,
    }
