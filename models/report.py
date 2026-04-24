"""Impact report data model."""

from dataclasses import dataclass, field


@dataclass
class ImpactReport:
    cve_id: str
    verdict: str  # "affected" | "not_affected" | "under_investigation"
    severity: str  # "critical" | "high" | "medium" | "low"
    affected_instances: list[dict] = field(default_factory=list)
    affected_repos: list[dict] = field(default_factory=list)
    remediation_steps: list[str] = field(default_factory=list)
    recommended_timeline: str = ""
    pr_id: str | None = None
    patch_status: str = "pending"  # "pending" | "applied" | "verified" | "failed"
    exploit_blocked: bool | None = None
