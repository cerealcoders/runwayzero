import json
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _required_env(monkeypatch):
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_INSTANCE_ID", "i-test1234567890abc")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_HOST", "10.0.0.1:8080")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_ROLE_NAME", "test-instance-role")
    monkeypatch.setenv("RUNWAYZERO_APP_MODULE_DIR", "/tmp/test-app-dir")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("GENSPARK_API_KEY", "gs-test")


@pytest.fixture
def cached_genspark_response(tmp_path: Path) -> Path:
    payload = {
        "cves": [
            {
                "id": "CVE-2026-33626",
                "cvss": 7.5,
                "ecosystem": "pypi",
                "package": "lmdeploy",
                "affected_range": "<= 0.12.2",
                "fixed_version": "0.12.3",
                "exploitation_status": "no public PoC",
                "summary": "SSRF in lmdeploy.vl.utils.load_image() allows fetching internal URLs (incl. IMDS).",
                "source_urls": ["https://github.com/advisories/GHSA-6w67-hwm5-92mq"],
            }
        ],
        "queried_at": "2026-04-23T00:00:00Z",
    }
    cache_file = tmp_path / "genspark-CVE-2026-33626.json"
    cache_file.write_text(json.dumps(payload))
    return cache_file
