import json

import pytest
import responses

from runwayzero_agent.tools.verify import (
    verify_service_healthy,
    verify_exploit_blocked,
)


@pytest.mark.asyncio
@responses.activate
async def test_verify_service_healthy_returns_healthy_on_200():
    responses.add(
        responses.GET, "http://10.0.0.1:8080/healthz",
        json={"status": "ok"}, status=200,
    )
    result = await verify_service_healthy({
        "url": "http://10.0.0.1:8080/healthz", "timeout_s": 5,
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["healthy"] is True
    assert payload["status_code"] == 200


@pytest.mark.asyncio
@responses.activate
async def test_verify_exploit_blocked_when_400_returned():
    responses.add(
        responses.POST, "http://10.0.0.1:8080/chat",
        json={"detail": "image rejected: blocked"}, status=400,
    )
    result = await verify_exploit_blocked({
        "url": "http://10.0.0.1:8080/chat",
        "payload": {"image_url": "http://169.254.169.254/latest/meta-data/"},
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["blocked"] is True
    assert payload["status_code"] == 400


@pytest.mark.asyncio
@responses.activate
async def test_verify_exploit_blocked_when_iam_creds_in_response():
    """200 with IAM credential markers — definitely NOT blocked."""
    responses.add(
        responses.POST, "http://10.0.0.1:8080/chat",
        json={"loaded": True, "preview": "{\"AccessKeyId\": \"AKIA...\"}"},
        status=200,
    )
    result = await verify_exploit_blocked({
        "url": "http://10.0.0.1:8080/chat",
        "payload": {"image_url": "http://169.254.169.254/latest/meta-data/"},
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["blocked"] is False


@pytest.mark.asyncio
@responses.activate
async def test_verify_exploit_blocked_when_2xx_without_markers_is_inconclusive():
    """200 with non-cred body is suspicious — treat as not-blocked per strict contract."""
    responses.add(
        responses.POST, "http://10.0.0.1:8080/chat",
        json={"loaded": True, "preview": "<garbage>"}, status=200,
    )
    result = await verify_exploit_blocked({
        "url": "http://10.0.0.1:8080/chat",
        "payload": {"image_url": "http://169.254.169.254/latest/meta-data/"},
    })
    payload = json.loads(result["content"][0]["text"])
    assert payload["blocked"] is False
    assert "inconclusive" in payload.get("note", "").lower() or payload["status_code"] == 200
