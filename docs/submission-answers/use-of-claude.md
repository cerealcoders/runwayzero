## Use of Claude

Claude (Anthropic) is the **reasoning and orchestration engine** at the heart of RunwayZero. It powers three critical capabilities:

### 1. Agent Orchestration

RunwayZero is built on the **Claude Agent SDK** with an in-process MCP (Model Context Protocol) server. Claude decides which tools to call, in what order, and how to interpret their results. The entire vulnerability triage — from detection to remediation — is driven by Claude's reasoning loop.

### 2. Impact Analysis & Decision-Making

After Genspark returns enriched CVE data and SSM returns infrastructure state, Claude:

- **Correlates** the affected version range against installed versions to determine if an instance is vulnerable
- **Assesses severity** by combining CVSS score, exploitation status, and the specific context of our environment
- **Decides the remediation path** — whether to create a PR only, or also hot-patch running instances (for critical, actively-exploited CVEs)
- **Reasons transparently** — the agent streams its reasoning to stdout so operators can follow the logic

### 3. Report Generation

Claude generates **structured, team-specific impact reports** that include:

- **Verdict** — affected / not affected / under investigation
- **Affected resources** — specific instance IDs, package versions, repository paths
- **Severity context** — not just the CVSS score, but what it means for *this* team's infrastructure
- **Remediation steps** — concrete actions with exact version numbers
- **Response timeline** — recommended urgency based on exploitation status

### Integration Architecture

```
Claude Agent SDK
├── System prompt (agent/prompts/system.md)
├── MCP server with 11 tools
│   ├── Genspark research
│   ├── SSM inventory + run command
│   ├── CodeCommit file ops + PR lifecycle
│   ├── Sandbox test runner
│   └── Exploit verification
└── Streaming output → operator console
```

### Why Claude

The vulnerability triage workflow requires **judgment, not just pattern matching**. Claude can reason about version ranges, weigh severity against context, decide when auto-remediation is appropriate, and explain its decisions — making it the right foundation for a security operations agent.
