# Security Policy

## Reporting a Vulnerability

Please report vulnerabilities privately via GitHub Security Advisories:

- https://github.com/tannernicol/helm-suite/security/advisories/new

Include:

- Affected version/commit
- Reproduction steps
- Expected vs actual behavior
- Impact and suggested mitigation

## Scope

In scope:

- Code and configuration templates in this repository
- Bootstrap and audit scripts
- Documentation patterns that can cause insecure deployments

Out of scope:

- Vulnerabilities in upstream third-party images/services
- Security issues caused by local deployment misconfiguration
- Private/internal extensions not present in this repository

## Public Hygiene

Never publish real credentials, internal domains, private IPs, or customer data in issues, PRs, docs, or examples.
