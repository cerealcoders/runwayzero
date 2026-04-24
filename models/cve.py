"""CVE enrichment data model."""

from dataclasses import dataclass


@dataclass
class CVEDetail:
    id: str
    cvss: float
    ecosystem: str  # e.g. "PyPI", "npm"
    package: str
    affected_range: str  # e.g. "<= 0.12.2"
    fixed_version: str  # e.g. "0.12.3"
    exploitation_status: str  # e.g. "active", "poc", "none"
    summary: str
    source_urls: list[str]
