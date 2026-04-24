# RunwayZero — An AI-Powered Vulnerability Impact Agent

**Date:** 2026-04-24
**Event:** Push to Prod Hackathon · Anthropic × Genspark · Singapore · April 2026
**Team:** Sourav · Kheng Wei · Eugene (SIA Cloud & Platforms / DevOps)

## 1. Vision

When a CVE drops, every team is left to investigate their own exposure manually — cross-referencing advisories against their infrastructure and codebases with no shared intelligence and no fast path to an answer. Meanwhile, AI-enabled attackers can weaponise a vulnerability within minutes of disclosure. The enterprise no longer has hours to spare.

**RunwayZero** is named on one principle: *no vulnerable package should get a clear runway into production.*

It is an AI agent that continuously monitors CVE feeds, scans all packages and binaries running across the environment — application and infrastructure layers, across all cloud providers — and informs each team exactly whether they are affected and what to do about it. It maps upstream and downstream dependencies to measure blast radius, enriches CVE data with stable version recommendations aligned to the organisation's pinning policy, and generates team-specific remediation guidance.

### Core Capabilities

1. **CVE Feed Ingestion** — Subscribes to RSS/advisory feeds from NVD, GitHub Security Advisories, and ecosystem-specific sources. The moment a vulnerability is published, RunwayZero begins triage automatically.

2. **Research & Enrichment (Genspark)** — Retrieves full vulnerability details: affected package versions, exploitation status, CVSS scoring, and stable migration paths. Genspark's research capabilities replace hours of manual advisory reading.

3. **Infrastructure Scanning (AWS SSM Inventory)** — Cross-references vulnerable packages against the team's live infrastructure. Identifies affected EC2 instances, OS versions, and installed packages in real time.

4. **Code Repository Scanning (AWS CodeCommit)** — Scans application and platform repositories for declared dependencies (requirements.txt, package.json, pom.xml, go.mod, etc.) to catch vulnerabilities that exist in code but may not yet be deployed.

5. **Owner Identification** — Resolves affected resources to responsible teams using AWS resource tags (App, Portfolio) and Project Catalog IDs in source code repositories. No blanket alerts — each team gets only what's relevant to them.

6. **Impact Report Generation (Claude)** — Produces structured, team-specific reports: verdict, affected resources, severity context, remediation steps, and recommended response timeline. Every team gets a consistent, expert-level starting point for response.

7. **Automated Remediation** — Goes beyond alerting. Creates a feature branch with the fix, opens a pull request, and asks the application team to review, test, and promote. This saves teams the manual effort of patching — they can go straight to functional testing.

8. **Version Pinning Enforcement** — Ensures no source code uses floating version references (`latest`, `^`, `~`, `*`). Enforces exact version pinning aligned to the organisation's policy. Recommends the correct version to pin based on what's actually running in production, preventing supply chain attacks (ref: Axios incident).

9. **SBOM Registry** — Maintains a persistent inventory of all libraries and packages across the ecosystem, their current versions, and compliance status. Only recommends updates when there is a security advisory — not for every new release — preventing unnecessary churn and supply chain risk.

10. **Dashboard UI** — A web interface where application teams select their application and portfolio from a dropdown and visualise all binaries and packages in use, their current versions, and compliance status.

### End Users

- **Application Owners** — Receive targeted vulnerability alerts and automated remediation PRs
- **Platform Team** — Visibility into infrastructure-level package exposure
- **CCoE (Cloud Centre of Excellence)** — Maintains and operates the system

### Value

- Reduces vulnerability triage from hours to under 60 seconds
- Directly addresses "rapid patch deployment" and "proactive AI-assisted threat hunting" readiness requirements
- Enables teams to respond at AI speed — matching the pace of the threat

---

## 2. Hackathon Demo Goal

Demonstrate an end-to-end agent that, in under three minutes of live stage time:

1. Detects a real, recently-disclosed CVE affecting a real package on a real EC2 instance in KrisCloud.
2. Reasons about impact and ownership.
3. Opens a CodeCommit pull request with the fix, runs tests against the patched version, and auto-merges on green.
4. Hot-patches the running EC2 in place via SSM Run Command.
5. Verifies the exploit path is closed by re-running the live exploit.

The "wow moment" is the closed loop: same `curl` command run twice on stage — first returns AWS IAM credentials, second is blocked.

## 3. The CVE

**CVE-2026-33626** — SSRF in `lmdeploy` (LLM serving framework).

| Field | Value |
|---|---|
| Advisory | GHSA-6w67-hwm5-92mq |
| CVSS v3.1 | 7.5 (High) |
| Affected | `lmdeploy <= 0.12.2` (PyPI) |
| Fixed | `lmdeploy == 0.12.3` |
| Root cause | `load_image()` in `lmdeploy/vl/utils.py` fetches arbitrary URLs without validating internal/private IPs |
| Exploit | POST to `/v1/chat/completions` with `image_url=http://169.254.169.254/...` returns AWS IMDS data |
| Disclosed | 2026-04-21 (two days before demo) |

Both vulnerable (0.12.2) and fixed (0.12.3) versions are confirmed installable via pip.

**Why this CVE:** AI/ML library (resonates with the audience), the SSRF target is the EC2 metadata service (concrete AWS-context stakes — "we just stole IAM creds"), single-line version-bump fix, recent enough to be genuinely topical.

## 4. Scope (in / out)

### In scope — built and live during demo

| Component | Implementation |
|---|---|
| **Agent orchestrator** | Python module using Claude Agent SDK with in-process MCP server |
| **Genspark research** | Real API call (replaces the deck's separate CVE feed + enrichment phases) |
| **SSM Inventory scan** | `boto3.ssm` via `sia-nonprod-auto2` profile |
| **CodeCommit auto-PR flow** | `boto3.codecommit` via `saml` profile: get_file → put_file (new branch) → create_pull_request → merge_pull_request |
| **Test execution** | `subprocess` running pytest in the agent's local sandbox against `lmdeploy==0.12.3` |
| **In-place SSM Run Command patch** | `boto3.ssm.send_command` to `pip install lmdeploy==0.12.3 && systemctl restart runwayzero-demo` on test-ec2 |
| **Live exploit verification** | `requests.get` against the test-ec2 chat endpoint with IMDS URL, before and after |
| **Vulnerable target app** | New ansible role `runwayzero-demo` in demo-app deploys a tiny FastAPI service that wraps `lmdeploy.vl.utils.load_image()` |

### Voice-over only — described in deck, not built for live demo

- Code Repo Scan for declared deps (SSM Inventory finding is sufficient for our chosen CVE)
- Owner resolution via AWS resource tags (App, Portfolio) and Project Catalog IDs (hardcoded to "eugene / demo-app team" for demo)
- Formal six-section App and Platform Team Reports (Claude's output is shown raw)
- Teams notification (skipped to save demo time; deck shows the Adaptive Card mockup)
- EventBridge 4-hour cron (manually triggered for stage control)

### Core features — designed, not yet implemented

These are integral to the RunwayZero vision (see §1) and will be built post-hackathon:

| Feature | Description |
|---|---|
| **CVE Feed Subscription** | RSS/webhook ingestion from NVD, GitHub Security Advisories, ecosystem feeds — auto-triggers the agent on new disclosures |
| **Code Repository Scanning** | Scan CodeCommit repos for declared dependencies (requirements.txt, package.json, pom.xml, go.mod, etc.) to catch vulnerabilities in code not yet deployed |
| **Version Pinning Enforcement** | Detect floating version references (`latest`, `^`, `~`, `*`) in source code; recommend exact version to pin based on running infrastructure state; prevent supply chain attacks |
| **SBOM Registry** | Persistent inventory of all libraries/packages across the ecosystem with current versions; only recommend updates on security advisories, not every new release |
| **Owner Resolution** | Automated lookup of application/platform owners via AWS resource tags (App, Portfolio) and Project Catalog IDs in repositories |
| **Dashboard UI** | Web interface for application teams to select their app/portfolio and visualise all packages, versions, and compliance status |
| **Multi-ecosystem support** | npm, Maven, Go, Ruby, Gradle in addition to PyPI |
| **Bitbucket integration** | Support for repos hosted outside CodeCommit |
| **Production IAM wiring** | Cross-account execution-role assume for Lambda-based deployment |

## 5. Architecture (Demo)

```
┌─────────────────────┐
│  Demo trigger       │ ← presenter runs `python agent.py CVE-2026-33626`
└──────────┬──────────┘
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  RunwayZero Agent  (Python · Claude Agent SDK · runs LOCALLY)    │
│                                                                  │
│  ClaudeSDKClient with in-process MCP server `runwayzero`         │
│  exposes 11 tools (see §7).                                      │
│                                                                  │
│  Streams selected events to stdout (tool name + input, tool      │
│  result summary, final reasoning) so the audience sees agent     │
│  behaviour without raw model chain-of-thought noise.             │
└──────────────────────────────┬──────────────────────────────────┘
                               │ uses local AWS profiles
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tool surfaces                                                   │
│                                                                  │
│  ├─ Genspark API           (https, API key from env)             │
│  ├─ Anthropic API          (Claude Agent SDK handles this)       │
│  ├─ CodeCommit (saml profile, account 817929577935)              │
│  └─ SSM (sia-nonprod-auto2 profile, account 837266371638)        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Target: demo-app · branch `eugene` · account nonprod-auto2      │
│                                                                  │
│  test-ec2 (Amazon Linux 3, t3.small, private subnet)             │
│  ├─ systemd: runwayzero-demo.service                             │
│  ├─ FastAPI on :8080 — POST /chat with image_url                 │
│  └─ Python venv with lmdeploy==0.12.2  ← vulnerable              │
│                                                                  │
│  CodeCommit repo: demo-app                                       │
│  └─ platform/files/runwayzero/requirements.txt  ← agent edits    │
└─────────────────────────────────────────────────────────────────┘
```

Production architecture (slide-only): the same `agent.py` exposes a `lambda_handler` so the entry point is identical when packaged as a Lambda triggered by EventBridge in a CCoE/shared-services account, with cross-account IAM execution-role assume into saml (CodeCommit) and the target app account (SSM).

## 6. Data flow (Demo)

1. Presenter invokes `python agent.py CVE-2026-33626`.
2. Agent calls `genspark_research(sbom=...)`. Returns enriched advisory: affected range, fixed version, exploitation status, safe migration path.
3. Agent calls `ssm_inventory_scan(package="lmdeploy")`. Returns one match: `{instance_id: i-xxx, version: 0.12.2, env: nonprod}`.
4. Claude reasons in-line: "lmdeploy 0.12.2 ≤ 0.12.2, vulnerable, fix is 0.12.3" — printed to stdout.
5. **[Live exploit, on stage]** presenter runs:
   ```
   curl -s test-ec2:8080/chat -d '{"image_url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/Ec2InstanceProfile"}'
   ```
   Returns IAM credentials JSON. **These are nonprod-auto2 credentials scoped to the test-ec2 instance role only** — the role is intentionally minimal (no production access). The credentials remain visible on stage for impact; voice-over confirms they are nonprod and short-lived.
6. Agent calls `codecommit_get_file(path="platform/files/runwayzero/requirements.txt", branch="eugene")` → reads `lmdeploy==0.12.2`.
7. Agent calls `codecommit_put_file(path=..., branch="runwayzero/cve-2026-33626", content="lmdeploy==0.12.3", parent_commit=...)` → creates the branch in one call.
8. Agent calls `codecommit_create_pull_request(title=..., source="runwayzero/cve-2026-33626", dest="eugene")`.
9. Agent calls `run_tests_in_sandbox(requirements="lmdeploy==0.12.3", test_path="tests/runwayzero/test_ssrf.py")` → returns pass/fail + stdout.
10. Agent calls `codecommit_post_pr_comment(pr_id, body=test_output)`.
11. Agent calls `codecommit_merge_pull_request(pr_id, merge_strategy="FAST_FORWARD")`. **Merge model:** the agent decides to merge based on its own test-runner result. No CodeCommit-side approval rules or required status checks are configured for the demo branch.
12. **In parallel with steps 8–11:** agent calls `ssm_run_command(instance_id="i-xxx", commands=["/opt/runwayzero/venv/bin/pip install --no-index --find-links /var/cache/runwayzero/wheels lmdeploy==0.12.3", "systemctl restart runwayzero-demo"])`. Targets the **service's exact venv** (not ambient shell python) so the patched library is the one the systemd unit imports on restart. Polls until success (~30s with pre-cached wheel).
13. **Post-patch health check (before second curl):** agent calls `verify_service_healthy(url=http://test-ec2:8080/healthz)` to confirm the FastAPI service restarted into the patched venv and is listening. This separates "exploit blocked because patched" from "exploit blocked because service is dead." If health check fails, agent halts and surfaces the failure rather than letting the audience see a misleading "blocked" result.

14. **[Live verification, on stage]** presenter re-runs the same curl from step 5 → blocked / 400.
15. Agent calls `verify_exploit_blocked(url=...)` → confirms programmatically (alongside the on-stage curl, captured in agent audit trail).
16. Agent calls `ssm_inventory_scan(package="lmdeploy")` again — **supplemental evidence only**. SSM Inventory has cache lag and may still report 0.12.2 for several minutes; the primary proof of patch is steps 13 + 14 (healthy service + blocked exploit). Voice-over acknowledges the lag honestly.
17. Agent prints final summary: "PR #N merged. Live host patched. Exploit blocked. Background: Step Function deploy of merged main will permanently bake the fix into the next AMI."

## 7. Tool inventory

Eleven tools, exposed as one in-process MCP server `runwayzero`. Each tool returns a structured payload (Python dict serialised to JSON in the MCP response). Schemas below are normative — implementation must conform. Tool references in other sections (e.g., §6, §7) use these names.

| Tool | Profile | Return schema (success) |
|---|---|---|
| `genspark_research(sbom: list[str]) → dict` | Genspark API key | `{cves: [{id, cvss, ecosystem, package, affected_range, fixed_version, exploitation_status, summary, source_urls}], queried_at}` |
| `ssm_inventory_scan(package: str) → dict` | `sia-nonprod-auto2` | `{matches: [{instance_id, package, version, app_tag, environment, freshness_ts}], inventory_age_seconds}` |
| `codecommit_get_file(repo, branch, path) → dict` | `saml` | `{content: str, blob_id, parent_commit_id, branch_head_commit_id}` |
| `codecommit_put_file(repo, branch, path, content, parent_commit_id, source_branch) → dict` | `saml` | `{commit_id, branch, branch_existed_before: bool}` (creates branch if absent) |
| `codecommit_create_pull_request(repo, title, source_branch, dest_branch, description) → dict` | `saml` | `{pr_id, status, web_url}` |
| `codecommit_post_pr_comment(repo, pr_id, body) → dict` | `saml` | `{comment_id}` |
| `codecommit_merge_pull_request(repo, pr_id, strategy) → dict` | `saml` | `{merged: bool, merge_commit_id, post_merge_branch_head}` |
| `run_tests_in_sandbox(requirements: str, test_path: str, timeout_s: int) → dict` | (local subprocess) | `{passed: bool, summary, stdout_tail, stderr_tail, duration_s}` |
| `ssm_run_command(instance_id, commands: list[str], timeout_s: int) → dict` | `sia-nonprod-auto2` | `{status, command_id, exit_code, stdout_tail, stderr_tail, duration_s}` |
| `verify_service_healthy(url: str, timeout_s: int) → dict` | (local) | `{healthy: bool, status_code, response_ms}` |
| `verify_exploit_blocked(url: str, payload: dict) → dict` | (local) | `{blocked: bool, status_code, response_body_preview}` |

Failure return shape (any tool): `{"error": str, "retryable": bool, "details": dict}`. The agent's system prompt instructs Claude to read `error` and `retryable` and decide whether to retry, fall back, or surface to the operator.

`verify_exploit_blocked` runs programmatically alongside the on-stage curl so the result is captured in the agent's audit trail, not just witnessed by the audience. `verify_service_healthy` runs between the patch and the second curl to distinguish "exploit blocked because patched" from "exploit blocked because service died."

## 8. Repository changes

### `~/KrisCloud/Repos/demo-app` (branch: `eugene`)

New files added before demo day:

```
platform/ansible/roles/runwayzero-demo/
  tasks/main.yml                # python3 -m venv /opt/runwayzero/venv
                                # /opt/runwayzero/venv/bin/pip install -r requirements.txt
                                # drop FastAPI app to /opt/runwayzero/app.py
                                # install /etc/systemd/system/runwayzero-demo.service, enable + start
  files/
    app.py                      # FastAPI service wrapping lmdeploy.vl.utils.load_image()
                                # exposes POST /chat (vulnerable endpoint) and GET /healthz
    runwayzero-demo.service     # systemd unit:
                                #   User=runwayzero
                                #   WorkingDirectory=/opt/runwayzero
                                #   ExecStart=/opt/runwayzero/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
platform/files/runwayzero/
  requirements.txt              # lmdeploy==0.12.2  ← agent edits this file
tests/runwayzero/
  test_ssrf.py                  # pytest: spins up app in-process, hits POST /chat with IMDS URL,
                                # asserts blocked when running fixed version. Mirrors the live curl
                                # path so green tests prove the same surface the stage curl hits.

# Also: temporary modification to ec2.yaml for demo only
platform/components/ec2.yaml    # set MetadataOptions.HttpTokens: optional (IMDSv1 enabled)
                                # so the SSRF exploit can read IMDS. Reverted post-demo.
```

Plus include `runwayzero-demo` role in `platform/ansible/ansible.yml`. The existing `demo-awslinux` role stays.

### New repo `runwayzero-agent` (or folder under hackathon dir)

```
runwayzero-agent/
├── agent.py              # entry point — both CLI and Lambda handler
├── tools/
│   ├── __init__.py
│   ├── genspark.py
│   ├── ssm.py            # ssm_inventory_scan, ssm_run_command
│   ├── codecommit.py     # all five CC tools
│   ├── sandbox.py        # run_tests_in_sandbox
│   └── verify.py         # verify_exploit_blocked
├── prompts/
│   └── system.md         # Claude's role + per-tool guidance
├── tests/
│   └── test_agent.py     # agent dry-run against mocked AWS
├── pyproject.toml
└── README.md
```

## 9. Live-demo timing budget

| Step | Target | Failure mode → mitigation |
|---|---|---|
| 1–4 (detect → reason → scan) | 30 s | Genspark API slow → use cached enrichment fallback baked into the tool |
| 5 (live exploit curl) | 5 s | EC2 unreachable → cut to pre-recorded video |
| 6–11 (PR flow + tests + merge) | 30 s | CodeCommit auth fails → agent prints diff to stdout; no merge |
| 12 (SSM Run Command) | 30–60 s | pip install slow → wheel pre-cached on EC2 |
| 13 (live verify curl) | 5 s | Still vulnerable → cut to pre-recorded video |
| 14–16 (re-scan + summary) | 15 s | SSM Inventory cache lag → voice-over the limitation |
| **Total live** | **~2–3 min** | |

## 10. Pre-demo setup checklist (run once, well before demo day)

1. Confirm both AWS profiles work: `aws sts get-caller-identity --profile saml` and `--profile sia-nonprod-auto2`.
2. Add the four `runwayzero-demo` files to `~/KrisCloud/Repos/demo-app` on branch `eugene`. Edit `platform/components/ec2.yaml` to set `MetadataOptions.HttpTokens: optional` (enables IMDSv1, required for the SSRF exploit to read IMDS). Push and wait for full Step Function deploy.
3. **Network reachability — must be confirmed, not assumed.** From the exact laptop you will demo on, verify `curl -v http://<test-ec2-private-ip>:8080/healthz` returns 200. If it doesn't (private subnet, no bastion routing, missing security group ingress), resolve before any other step — no fallback covers a non-reachable target. Document the exact path (direct VPC, bastion, VPN) in this doc once confirmed.
4. SSH/SSM into test-ec2 once and pre-cache the lmdeploy 0.12.3 wheel: `pip download lmdeploy==0.12.3 -d /var/cache/runwayzero/wheels/`. Confirm the `ssm_run_command` install path `/opt/runwayzero/venv/bin/pip install --no-index --find-links /var/cache/runwayzero/wheels lmdeploy==0.12.3` works in under 30s.
5. **Verify the patch actually closes the exploit, end-to-end, on the real host.** From the demo workstation: confirm exploit succeeds with 0.12.2, then SSM-patch to 0.12.3, restart service, confirm `/healthz` 200, confirm exploit now blocked. This proves Codex's #1 risk does not bite on stage.
6. Pre-cache a Genspark response for CVE-2026-33626 on disk; the `genspark_research` tool falls back to it on API failure.
7. Get Genspark API credentials and Anthropic API key into local env (`.env`, gitignored).
8. Dry-run the entire agent flow against the live EC2 the day before demo. Capture the output — that becomes the pre-recorded fallback video.
9. Run the §14 reset procedure to restore demo-ready state after every dry run.

## 11. Fallback strategy

| Failure during live demo | Fallback action |
|---|---|
| Genspark API down | Tool serves cached response, agent continues |
| CodeCommit auth fails | Agent prints diff to stdout, narrator says "in production this would PR — let's continue" |
| SSM Run Command times out | Skip live verification, narrator pivots to "the merged PR will deploy in the background" |
| Verify-blocked still returns IMDS | Cut to pre-recorded video at this point |
| Catastrophic | Cut to pre-recorded video from the start |

## 12. Production Architecture (deck-only)

The same `agent.py` exposes a `lambda_handler(event, context)` entry point. In production, the full RunwayZero flow operates as follows:

### Trigger Layer
- **CVE Feed Ingestion** — RSS/webhook subscriptions to NVD, GitHub Security Advisories, and ecosystem feeds. New advisories trigger the agent automatically via EventBridge rules.
- **Scheduled Scan** — EventBridge cron (every N hours) triggers a full inventory reconciliation as a safety net.
- **On-Demand** — CCoE or application teams can trigger a scan for a specific CVE manually.

### Agent Execution
- Lambda → `lambda_handler({"trigger": "cve_feed", "cve_id": "CVE-XXXX-XXXXX"})`
- **Genspark enrichment** — Research affected packages, versions, exploitation status, safe migration paths
- **Infrastructure scan** — SSM Inventory across all target accounts to identify affected instances and packages
- **Code repo scan** — Scan CodeCommit repositories for declared dependencies (requirements.txt, package.json, pom.xml, go.mod, etc.)
- **Owner resolution** — Map affected resources to responsible teams via AWS resource tags (App, Portfolio) and Project Catalog IDs
- **Impact report** — Claude generates team-specific, structured reports with verdict, affected resources, severity, and remediation steps

### Remediation Layer
- **Automated PR** — Creates a feature branch with the version fix, opens a PR, and notifies the application team to review, test, and promote (not auto-merge in production)
- **Team notification** — Teams channel via webhook or Adaptive Card via Power Automate
- **Hot-patch (optional)** — For critical/actively-exploited CVEs, SSM Run Command can patch running instances immediately while the PR follows the standard review process

### Cross-Account Access
- Lambda assumes a cross-account role into `saml` for CodeCommit operations
- Lambda assumes a cross-account role into target app accounts for SSM operations

### Persistent State
- **SBOM Registry (DynamoDB)** — Caches package inventory across all applications, tracks current versions, compliance status. Only recommends updates on security advisories, not every new release.
- **Version Pinning Policy** — Continuous enforcement: flags any source code using floating version references (`latest`, `^`, `~`, `*`) and recommends exact versions based on running infrastructure state.

### Dashboard UI
- Web interface for application teams to select their app/portfolio and visualise all packages, versions, and compliance status
- CCoE view for cross-organisation vulnerability posture

None of the production wiring is built. It is described and diagrammed in the deck.

## 13. Demo-critical assumptions

These must all be true on stage. Pre-demo checklist (§10) verifies each one:

1. **Test-ec2 has IMDSv1 enabled** (`HttpTokens: optional`) — otherwise the SSRF GET cannot read IMDS and the dramatic "stole IAM creds" moment fails.
2. **The vulnerable code path is exploitable in our exact wrapper.** `lmdeploy 0.12.2` `load_image()` called from our FastAPI `POST /chat` handler returns IMDS body content to the response. Verified by §10 step 5.
3. **The fix actually closes the exploit through the same wrapper.** `lmdeploy 0.12.3` blocks IMDS URLs at `load_image()` and our handler surfaces a non-success status. Verified by §10 step 5.
4. **Network reachability** from demo workstation to `test-ec2:8080` is confirmed and stable (§10 step 3).
5. **The SSM patch targets the right venv.** `pip install` runs against `/opt/runwayzero/venv/bin/pip`, not ambient shell python. Systemd `ExecStart` uses `/opt/runwayzero/venv/bin/uvicorn`, so they share interpreter state.
6. **Pre-cached wheel for 0.12.3** is on test-ec2 at `/var/cache/runwayzero/wheels/`, so SSM patch finishes in ~30s (no network pip download).
7. **AWS profiles `saml` and `sia-nonprod-auto2` are valid** with sufficient permissions: CodeCommit (read/write/PR/merge on `demo-app` repo) and SSM (`GetInventory`, `SendCommand`, `GetCommandInvocation` on test-ec2).
8. **Genspark and Anthropic API keys** are loaded in env. Genspark cached response exists as fallback.

## 14. Rehearsal reset procedure

After every dry run, run this to restore the demo to a known starting state. Without it, the second dry run will fail (branch already exists, PR already merged, host already at 0.12.3).

```bash
# 1. Downgrade the host back to vulnerable
aws ssm send-command \
  --profile sia-nonprod-auto2 --region ap-southeast-1 \
  --instance-ids <test-ec2-id> \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["/opt/runwayzero/venv/bin/pip install lmdeploy==0.12.2", "systemctl restart runwayzero-demo"]'

# 2. Confirm exploit works again
curl -s http://<test-ec2>:8080/chat \
  -d '{"image_url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/Ec2InstanceProfile"}'
# Expect IAM creds in response.

# 3. Close any open PR from the agent
aws codecommit list-pull-requests --profile saml --region ap-southeast-1 \
  --repository-name demo-app --pull-request-status OPEN \
  --query "pullRequestIds" --output text \
| xargs -n1 -I{} aws codecommit update-pull-request-status \
  --profile saml --region ap-southeast-1 \
  --pull-request-id {} --pull-request-status CLOSED

# 4. Delete the agent's feature branch (if it exists)
aws codecommit delete-branch --profile saml --region ap-southeast-1 \
  --repository-name demo-app --branch-name runwayzero/cve-2026-33626 || true

# 5. Reset requirements.txt on eugene branch back to lmdeploy==0.12.2 (if a previous merge changed it)
#    Use git locally:
cd ~/KrisCloud/Repos/demo-app
git checkout eugene && git pull
# edit platform/files/runwayzero/requirements.txt back to lmdeploy==0.12.2 if needed
git commit -am "rehearsal reset" && git push origin eugene
```

This script should live as `runwayzero-agent/scripts/reset-demo.sh` and be runnable in one command.

## 15. What this design does NOT cover

- Implementation plan (file-by-file order, test-first cadence) — that's the next document
- Specific Genspark API request/response shape — to be confirmed once API access is in hand
- Specific Teams Adaptive Card payload — skipped for live demo
- Production IAM policies, cross-account trust relationships, Lambda packaging
- Dashboard UI framework/stack decision
- SBOM registry DynamoDB schema design
- Multi-ecosystem dependency parser implementations (npm, Maven, Go, Ruby, Gradle)
