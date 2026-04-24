# RunwayZero

**Autonomous CVE Remediation Agent** — built for the *Push to Prod* hackathon (Genspark × Claude).

RunwayZero is an AI-powered agent that detects a vulnerable dependency, traces its blast radius across your infrastructure, patches the code, runs tests, hot-patches the live host, and proves the exploit is closed — all without human intervention.

---

## How it works

When triggered with a CVE identifier, RunwayZero executes a 14-step end-to-end pipeline powered by the Anthropic tool-use API (`claude-opus-4-7`):

| Step | Action | Tool |
|------|--------|------|
| 1 | Query Genspark threat intel to confirm affected version and fix | `genspark_research` |
| 2 | Scan AWS SSM inventory to find all instances running the vulnerable package | `ssm_inventory_scan` |
| 3 | Scan CodeCommit source code to find every file that imports the package | `codecommit_get_file` |
| 4 | Assess blast radius and identify owning team | Agent reasoning |
| 5 | Read the current `requirements.txt` from CodeCommit | `codecommit_get_file` |
| 6 | Mutate the file — bump the vulnerable version to the patched version | Agent reasoning |
| 7 | Push the fix to a new feature branch and open a Pull Request | `codecommit_put_file` + `codecommit_create_pull_request` |
| 8 | Run the full test suite in an ephemeral sandbox venv | `run_tests_in_sandbox` |
| 9 | Post test results as a PR comment | `codecommit_post_pr_comment` |
| 10 | If tests pass, notify the application team via MS Teams with a deployment link | Agent reasoning |
| 11 | Hot-patch the live EC2 instance from a pre-cached wheel directory | `ssm_run_command` |
| 12 | Verify the service is healthy after the patch | `verify_service_healthy` |
| 13 | Confirm the SSRF exploit is now blocked | `verify_exploit_blocked` |
| 14 | Print a final summary: PR URL, instance patched, exploit verdict | Agent reasoning |

> The feature branch deployment auto-triggers CI/CD. The application team tests the feature branch deployment and drives promotion to UAT → master. RunwayZero never merges to main.

---

## Demo scenario — CVE-2026-33626

| Field | Value |
|-------|-------|
| CVE | `CVE-2026-33626` |
| Package | `lmdeploy==0.12.2` |
| Vulnerability | SSRF via unvalidated `image_url` in `VL.decode()` — leaks AWS IAM credentials via IMDS |
| Fix | Upgrade to `lmdeploy==0.12.3` |
| Affected file | `app.py` — `from lmdeploy.vl import decode` |
| Feature branch | `runwayzero/cve-2026-33626` |

---

## Project structure

```
runwayzero/
├── runwayzero_agent/
│   ├── agent.py              # Orchestrator — Anthropic tool-use loop
│   ├── config.py             # Environment-based configuration
│   ├── tool_registry.py      # Tool registration and dispatch
│   ├── errors.py             # Standardised success/error response helpers
│   ├── prompts/
│   │   └── system.md         # Agent system prompt with 14-step flow
│   └── tools/
│       ├── codecommit.py     # Git operations via AWS CodeCommit
│       ├── genspark.py       # CVE enrichment via Genspark API
│       ├── sandbox.py        # Ephemeral venv test runner
│       ├── ssm.py            # AWS SSM inventory scan + remote command
│       └── verify.py         # Health check + exploit verification
├── assets/
│   ├── dashboard.html        # SBOM compliance dashboard (aviation theme)
│   └── flowchart.html        # Interactive 14-step pipeline diagram
├── tests/
├── pyproject.toml
└── README.md
```

---

## Prerequisites

- Python 3.11+
- AWS credentials configured with access to:
  - **CodeCommit** — read/write access to the target repository
  - **SSM** — `ssm:DescribeInstanceInformation`, `ssm:ListInventoryEntries`, `ssm:SendCommand`, `ssm:GetCommandInvocation`
- `ANTHROPIC_API_KEY` environment variable
- `GENSPARK_API_KEY` environment variable (optional — falls back to cached fixture)

---

## Installation

```bash
git clone https://github.com/cerealcoders/runwayzero.git
cd runwayzero
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

---

## Configuration

All runtime values are passed via environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key |
| `GENSPARK_API_KEY` | No | Genspark API key (falls back to cached fixture) |
| `RUNWAYZERO_TEST_EC2_INSTANCE_ID` | Yes | SSM-managed instance ID to hot-patch |
| `RUNWAYZERO_TEST_EC2_HOST` | Yes | Host and port of the running service e.g. `10.0.0.1:8080` |
| `RUNWAYZERO_TEST_EC2_ROLE_NAME` | Yes | IAM role name attached to the instance (used in IMDS exploit path) |
| `RUNWAYZERO_APP_MODULE_DIR` | Yes | Absolute path to the directory containing `app.py` |
| `AWS_REGION` | No | AWS region (default: `ap-southeast-1`) |
| `CODECOMMIT_AWS_PROFILE` | No | AWS profile for CodeCommit (default: `default`) |
| `SSM_AWS_PROFILE` | No | AWS profile for SSM (default: `default`) |
| `DEMO_APP_REPO` | No | CodeCommit repository name (default: `demo-app`) |
| `DEMO_APP_BRANCH` | No | Base branch (default: `main`) |
| `DEMO_APP_REQUIREMENTS_PATH` | No | Path to requirements file in repo (default: `requirements.txt`) |
| `RUNWAYZERO_GENSPARK_CACHE_DIR` | No | Override path for Genspark response cache |
| `RUNWAYZERO_TEST_PATH` | No | Path to pytest test file (default: `tests/test_ssrf.py`) |

---

## Running

**CLI:**
```bash
runwayzero-agent CVE-2026-33626
```

**AWS Lambda:**

Deploy the package and invoke with:
```json
{ "cve_id": "CVE-2026-33626" }
```

**Programmatic:**
```python
import asyncio
from runwayzero_agent.agent import run_pipeline

result = asyncio.run(run_pipeline("CVE-2026-33626"))
```

---

## Assets

### SBOM Compliance Dashboard

Open `assets/dashboard.html` in a browser — no server required.

- Portfolio / application / branch dropdowns
- Instrument gauges: total packages, vulnerable, critical CVEs, outdated, compliant
- Package table with current, recommended, and latest versions
- CVE chips linked to NVD advisories
- **Re-scan simulation**: step-through animation that patches all vulnerable packages and flips them to `PATCHED ✓` with an `RZ` badge — useful for demo walkthroughs
- Individual `⚡ Fix` button per vulnerable package
- Boarding-pass detail drawer with version info, CVE details, and code usage locations

### Pipeline Flowchart

Open `assets/flowchart.html` in a browser.

- Interactive 14-step pipeline diagram
- Click any node to see the tool used, input/output contract, and decision logic
- Decision forks for test failures and health check failures
- MS Teams notification nodes on all halt/failure paths
- Feature branch → CI/CD → team review → UAT → master promotion flow

---

## Architecture

```
Trigger (CVE ID)
      │
      ▼
┌─────────────────────────────────────┐
│         claude-opus-4-7             │
│   (Anthropic tool-use loop)         │
└──────────┬──────────────────────────┘
           │ tool calls
    ┌──────┼───────────────────────────────┐
    │      │                               │
    ▼      ▼                               ▼
Genspark  AWS (CodeCommit + SSM)     Target EC2
 API      ┌──────────────┐           ┌──────────┐
          │ requirements │           │ pip patch│
          │ .txt patched │           │ + restart│
          │ PR opened    │           └──────────┘
          └──────────────┘                │
                                          ▼
                                   verify_service_healthy
                                   verify_exploit_blocked
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | 0.97.0 | Claude API client |
| `boto3` | 1.42.61 | AWS SDK (CodeCommit, SSM) |
| `requests` | 2.32.5 | HTTP client (Genspark, health checks) |
| `anyio` | 4.13.0 | Async runtime |

---

## Hackathon

Built for the **Push to Prod** hackathon by Genspark and Claude.

> *"From detection to exploit-closed in one agentic loop."*
