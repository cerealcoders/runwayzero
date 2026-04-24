from runwayzero_agent.errors import error_response, success_response


def test_success_response_wraps_payload_for_mcp():
    out = success_response({"foo": 1, "bar": [2, 3]})
    assert "content" in out
    assert isinstance(out["content"], list)
    assert out["content"][0]["type"] == "text"
    import json
    assert json.loads(out["content"][0]["text"]) == {"foo": 1, "bar": [2, 3]}


def test_error_response_marks_is_error_and_includes_retryable_flag():
    out = error_response("network timeout", retryable=True, details={"code": "ETIMEDOUT"})
    assert out.get("is_error") is True
    import json
    payload = json.loads(out["content"][0]["text"])
    assert payload == {
        "error": "network timeout",
        "retryable": True,
        "details": {"code": "ETIMEDOUT"},
    }
