# Security Policy

CAPS Agent Security is intended for authorized defensive evaluation in synthetic or explicitly approved environments.

## Report a vulnerability

Use GitHub's private vulnerability reporting flow:

- https://github.com/Mutoy-choi/CAPS-Agent-Security/security/advisories/new

Include the affected release or commit, configuration fingerprint, minimal synthetic reproduction, expected and observed behavior, and evidence hashes. Do not include real credentials, customer files, production prompts, or destructive payloads.

If private vulnerability reporting is not available, contact the repository owner without publishing exploit details in a public issue.

## Coordinated disclosure

Please allow a reasonable remediation window before publishing a vulnerability that could materially affect users. High-severity findings involving a third-party model, Plugin, Skill, MCP server, or agent platform should also follow that provider's disclosure process.

## Supported versions

Until a stable public release is published, only the latest `main` commit and the active release candidate are supported.

## Safety boundaries

- Test only systems you own or are authorized to evaluate.
- Run active probes in synthetic sessions with fixture tools.
- Do not insert hidden jailbreak content into live user queries.
- Do not use real credentials, customer data, payments, or production side effects.
- Plugin and Skill installation does not authorize telemetry or data contribution.
