## Our Solution: RunwayZero

RunwayZero is an **AI agent that gives application teams an instant, evidence-based answer** to the question: *"Are we affected?"*

### How It Works

1. **CVE Detection** — The agent monitors vulnerability feeds (NVD, GitHub Security Advisories). The moment a new CVE is published, triage begins automatically.

2. **Research & Enrichment** — Using Genspark, the agent retrieves full vulnerability details: affected package versions, exploitation status, CVSS scoring, and safe migration paths.

3. **Infrastructure Scanning** — The agent queries AWS Systems Manager (SSM) Inventory to identify affected EC2 instances, installed package versions, and environment context — in real time.

4. **Code Repository Scanning** — Scans CodeCommit repositories for declared dependencies to catch vulnerabilities that exist in code but may not yet be deployed.

5. **Owner Resolution** — Maps affected resources to responsible teams using AWS resource tags (App, Portfolio) and Project Catalog IDs. No blanket alerts — each team gets only what's relevant to them.

6. **Impact Report** — Claude generates a structured, team-specific report: verdict, affected resources, severity context, remediation steps, and a recommended response timeline.

7. **Automated Remediation** — The agent creates a feature branch with the version fix, opens a pull request, and notifies the application team to review, test, and promote. For critical CVEs, it can also hot-patch running instances immediately via SSM.

### What Makes It Different

- **Proactive, not reactive** — teams don't search for risk; risk finds them
- **Evidence-based** — every alert comes with proof: instance IDs, versions, code paths
- **Actionable** — not just "you're affected" but "here's the PR with the fix"
- **Policy-aware** — enforces version pinning, tracks SBOM, only recommends security updates
