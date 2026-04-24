"""Verification tools — health check and exploit validation."""

import requests


def verify_service_healthy(url: str, timeout_s: int = 30) -> dict:
    """Check if the target service is up and responding.

    Returns:
        {healthy: bool, status_code, response_ms}
    """
    try:
        resp = requests.get(url, timeout=timeout_s)
        return {
            "healthy": resp.status_code == 200,
            "status_code": resp.status_code,
            "response_ms": int(resp.elapsed.total_seconds() * 1000),
        }
    except requests.RequestException as e:
        return {"error": str(e), "retryable": True, "details": {}}


def verify_exploit_blocked(url: str, payload: dict) -> dict:
    """Attempt the exploit and confirm it is blocked.

    Returns:
        {blocked: bool, status_code, response_body_preview}
    """
    try:
        resp = requests.post(url, json=payload, timeout=10)
        body_preview = resp.text[:200]
        # If we get IMDS-like content back, exploit is NOT blocked
        blocked = "AccessKeyId" not in body_preview
        return {
            "blocked": blocked,
            "status_code": resp.status_code,
            "response_body_preview": body_preview,
        }
    except requests.RequestException as e:
        return {"error": str(e), "retryable": True, "details": {}}
