# RunwayZero

**AI-powered vulnerability impact agent** — given a CVE, RunwayZero investigates which of your services are affected, patches the code, runs the test suite, opens the PR, hot-patches the live host, and verifies the exploit is closed. End to end, no human in the loop.

![RunwayZero dashboard](media/out/hero.gif)

---

## What it does

A new CVE drops. Today, that means a triage queue, a Jira ticket, a security engineer reading the advisory, a developer writing the bump, a reviewer approving it, a deploy, and someone manually proving the host is no longer exploitable. Hours to days.

RunwayZero collapses that into a single tool-using Claude agent:

1. **Research** — confirms the affected versions and the fix from a CVE database.
2. **Impact** — scans SSM inventory across the fleet to identify which instances run the vulnerable package.
3. **Patch** — opens the requirements file in CodeCommit, bumps the pinned version, pushes a fix branch.
4. **Test** — installs the patched dependencies in a sandbox and runs the project's test suite.
5. **Merge** — comments the test summary on the PR and (if green) merges fast-forward.
6. **Hot-patch** — runs `pip install` on the live EC2 over SSM, restarts the service.
7. **Verify** — replays the exploit against the running host and confirms it is now blocked.

Each step is a discrete tool exposed to Claude via the Anthropic tool-use API; the agent decides the order and handles the error paths.

## The dashboard

The dashboard (`assets/dashboard.html`) is the human-facing flight deck — a real-time view of every package across every service, with one-click access to the agent.

### Spot the risk

![Switch to Vulnerable to surface critical CVEs first](media/out/spot-risk.gif)

Filter to **Vulnerable** and the critical CVE rows surface first — sorted by severity, with the affected packages, their current pinned versions, and the recommended fixes side-by-side.

### Drill in

![Boarding-pass drawer reveals the CVE detail and where it bites](media/out/drill-in.gif)

Click any package to open the boarding-pass drawer: the CVE summary, the affected file paths and line numbers in your codebase, the recommended version bump, and the licence.

### Auto-remediate

![One click triggers the RunwayZero pipeline](media/out/auto-remediate.gif)

Hit **Auto-remediate with RunwayZero** and the agent kicks off — the steps above run autonomously. The dashboard surfaces the toast; the live status streams to stdout (or, in production, to whatever you wire it into).

## Architecture

```
runwayzero_agent/
  agent.py            # tool-use loop, model orchestration
  config.py           # env-driven runtime config
  tool_registry.py    # decorator-based tool registration
  tools/              # one module per capability
    genspark.py       # CVE database lookup
    ssm.py            # AWS SSM inventory + run-command
    codecommit.py     # AWS CodeCommit read/write/PR
    sandbox.py        # sandboxed pytest of patched deps
    verify.py         # exploit replay + health check
  prompts/system.md   # the agent's instructions (the demo flow)
assets/
  dashboard.html      # SBOM compliance UI (self-contained)
  flowchart.html      # pipeline diagram
```

The agent uses **Claude Opus 4.7** via the Anthropic SDK. Tools are registered via a small decorator (`tool_registry.register_tool`); the registry hands JSON Schema definitions to the model and dispatches the resulting `tool_use` blocks back to Python coroutines.

## Quickstart

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, AWS profile/region, target instance & host, …

# 3. Dry-run the demo
./scripts/dry-run.sh

# 4. Run for real (against a CVE)
runwayzero-agent CVE-2026-33626
```

The demo is wired around a single staged CVE (`CVE-2026-33626`, an SSRF in `lmdeploy`) and a target EC2 instance running a small FastAPI app — see `runwayzero_agent/prompts/system.md` for the exact flow the agent executes.

## Tests

```bash
pytest
```

`tests/` covers the tool layer (mocked AWS via `moto`, mocked HTTP via `responses`) and the sandboxed test runner.

## Status

Hackathon demo. The agent flow is hardcoded for the staged CVE; the dashboard data is in-memory mock SBOM data. The plumbing (tool registry, model loop, sandbox runner, AWS adapters, dashboard UI, and the GIF pipeline) is real.
