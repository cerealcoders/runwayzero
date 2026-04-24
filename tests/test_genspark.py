import json
from pathlib import Path

import pytest
import responses

from runwayzero_agent.tools.genspark import genspark_research


@pytest.fixture
def cache_dir(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv("RUNWAYZERO_GENSPARK_CACHE_DIR", str(tmp_path))
    payload = {
        "cves": [
            {
                "id": "CVE-2026-33626", "cvss": 7.5, "ecosystem": "pypi",
                "package": "lmdeploy", "affected_range": "<= 0.12.2",
                "fixed_version": "0.12.3", "exploitation_status": "no public PoC",
                "summary": "SSRF in load_image()",
                "source_urls": ["https://github.com/advisories/GHSA-6w67-hwm5-92mq"],
            }
        ],
        "queried_at": "2026-04-23T00:00:00Z",
    }
    (tmp_path / "genspark-CVE-2026-33626.json").write_text(json.dumps(payload))
    return tmp_path


@pytest.mark.asyncio
@responses.activate
async def test_genspark_research_returns_structured_payload(cache_dir):
    responses.add(
        responses.POST,
        "https://api.genspark.ai/v1/research",
        json={
            "cves": [
                {"id": "CVE-2026-33626", "cvss": 7.5, "ecosystem": "pypi",
                 "package": "lmdeploy", "affected_range": "<= 0.12.2",
                 "fixed_version": "0.12.3", "exploitation_status": "no public PoC",
                 "summary": "SSRF", "source_urls": []}
            ],
            "queried_at": "2026-04-23T00:00:00Z",
        },
        status=200,
    )
    result = await genspark_research({"sbom": ["lmdeploy==0.12.2"]})
    payload = json.loads(result["content"][0]["text"])
    assert payload["cves"][0]["id"] == "CVE-2026-33626"
    assert payload["cves"][0]["fixed_version"] == "0.12.3"


@pytest.mark.asyncio
@responses.activate
async def test_genspark_research_falls_back_to_cache_on_api_failure(cache_dir):
    responses.add(
        responses.POST, "https://api.genspark.ai/v1/research",
        body=ConnectionError("network down"),
    )
    result = await genspark_research({"sbom": ["lmdeploy==0.12.2"]})
    payload = json.loads(result["content"][0]["text"])
    assert payload["cves"][0]["id"] == "CVE-2026-33626"
    assert payload.get("from_cache") is True
