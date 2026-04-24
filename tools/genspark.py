"""Genspark CVE research and enrichment tool."""

import json
import os
from pathlib import Path

import requests

from agent.config import GENSPARK_API_KEY, CACHE_DIR


def genspark_research(sbom: list[str]) -> dict:
    """Research CVEs affecting the given packages via Genspark API.

    Falls back to cached response if API is unavailable.

    Returns:
        {cves: [{id, cvss, ecosystem, package, affected_range,
                 fixed_version, exploitation_status, summary, source_urls}],
         queried_at: str}
    """
    # TODO: Implement Genspark API call
    # Fallback: load cached response
    for package in sbom:
        cache_file = Path(CACHE_DIR) / f"genspark_{package}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())

    return {"error": "Genspark API not configured and no cached response found", "retryable": False, "details": {}}
