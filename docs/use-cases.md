# Use Cases

## SaaS Exit Planning
Use when mapping a migration from hosted tools to self-hosted alternatives.

Inputs:
- Current SaaS list
- Data export formats
- Target modules

Outputs:
- Migration plan
- Module map
- Risk notes

Notes:
- Verify exports before decommissioning tools.
- Prioritize high-value replacements first: docs, photos, search, finance, and source control.

### Recommended replication map
- Google Docs -> Notes App
- Google Photos -> Immich / Photos AI
- Google Search -> SearXNG + Homelab Search
- Mint -> Money App
- GitHub (personal repos) -> Gitea

## Local-First Personal Ops
Use when designing a private, integrated workflow stack.

Inputs:
- Workflow inventory
- Data boundaries
- Storage plan

Outputs:
- Stack architecture
- Security model
- Integration plan

Notes:
- Document trust boundaries early.
- Keep auth centralized with Authelia SSO + 2FA.
- Keep everything private-by-default behind Tailscale.

## Offline Coding Agent (Highlight)
Use when you want cloud-level coding assistant quality with local ownership.

Inputs:
- Claude/Codex session transcripts or coding patterns
- A local target model (for example, Pip-Boy)
- Evaluation prompts for quality checks

Outputs:
- Updated local coding-agent behavior aligned to your workflows
- Reduced recurring API dependency for repetitive tasks
- Private coding assistant capabilities that improve over time

Notes:
- This is a key differentiator for Helm Suite and should be surfaced in overview docs.

## Private Security Lab (On-Prem)
Use when demonstrating local vulnerability triage without exposing proprietary methods.

Inputs:
- Authorized targets (internal assets, CTF, HTB-style labs)
- Scanner and analyzer outputs
- Local storage for findings and remediation notes

Outputs:
- Private vulnerability triage workflow
- Faster local analysis feedback loop
- Evidence and notes retained on-prem

Notes:
- Keep wording explicitly scoped to authorized environments only.
- Show practical value, not proprietary bounty playbooks.

## Toolkit Reference Stack
Use when building your own suite of personal tools.

Inputs:
- Module list
- Routing plan
- UI conventions

Outputs:
- Blueprint docs
- Component map
- Roadmap

Notes:
- Keep public docs sanitized.
