## Use of Genspark

Genspark plays a critical role in RunwayZero's **CVE research and enrichment** phase — the first step after a vulnerability is detected.

### What Genspark Does in RunwayZero

When the agent receives a CVE notification, it calls Genspark's research API to:

1. **Retrieve full vulnerability details** — affected package names, version ranges, CVSS scores, and advisory sources
2. **Determine exploitation status** — whether the vulnerability is actively exploited in the wild, has a known proof-of-concept, or is theoretical
3. **Identify the safe migration path** — which exact version to upgrade to, considering backward compatibility and stability
4. **Aggregate from multiple sources** — NVD, GitHub Security Advisories, ecosystem-specific databases (PyPI, npm, Maven)

### Why Genspark

Manual CVE triage requires reading multiple advisory pages, cross-referencing version ranges, and making judgment calls about severity. Genspark replaces this **hours-long research process** with a single API call that returns structured, actionable intelligence.

### Integration Point

```
Agent detects CVE → Genspark researches → Returns enriched advisory
                                           ├── affected_range: "<= 0.12.2"
                                           ├── fixed_version: "0.12.3"
                                           ├── exploitation_status: "active"
                                           └── summary + source_urls
```

The enriched output feeds directly into Claude's reasoning engine, which then cross-references against live infrastructure to determine impact.

### Resilience

The agent caches Genspark responses locally so that if the API is unavailable during a live incident, previously researched CVEs can still be triaged without delay.
