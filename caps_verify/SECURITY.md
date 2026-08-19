# Security policy

CAPS Verify is for authorized defensive evaluation in synthetic or explicitly approved environments.

## Non-negotiable constraints

- Do not connect fixture tools to real email, cloud drive, CRM, payment, identity, or external HTTP systems.
- Do not store real credentials, tokens, customer records, or production prompts in benchmark artifacts.
- Use synthetic canaries and `fixture://` destinations.
- Do not publish private holdout attacks or a high-severity third-party bypass before coordinated disclosure.
- Treat Plugin hooks and prompt instructions as defense-in-depth, not as the sole security boundary.
- Put production enforcement in a fail-closed gateway with auditable policy decisions.

## Reporting a vulnerability

Open a private security advisory in the repository or contact the repository owner directly. Include the affected commit, configuration fingerprint, minimal synthetic reproduction, and evidence-bundle hashes.
