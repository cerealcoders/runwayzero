## The Problem

When a new CVE is published, **application teams have no fast, automated way to determine if they are affected.** Security teams send blanket alerts, and individual teams spend hours manually cross-referencing vulnerability advisories against their infrastructure and codebases.

### Why This Matters Now

Following a recent supply chain incident, our organisation issued a directive requiring all teams to:
- Audit dependencies across every codebase
- Pin exact library versions
- Eliminate auto-updates from all config files

That incident made one thing clear: **when a CVE drops, every team is left investigating their own exposure manually**, with no shared intelligence and no fast path to an answer.

### The Scale of the Problem

- Multiple application teams, each owning different stacks and infrastructure
- Hundreds of EC2 instances running various packages across environments
- Dozens of code repositories with declared dependencies
- No centralised view of what's running where, or who owns what

### The Threat

AI-enabled attackers can now weaponise a vulnerability **within minutes of disclosure**. The enterprise no longer has hours — or even a full day — to triage and respond. The gap between a CVE being published and a team knowing whether they need to act is the vulnerability itself.
