# Contributing to CAPS Unlock Lab

CAPS welcomes reproducible benchmarks, fixture environments, defensive controls, accessibility improvements, provider adapters, and documentation.

## Before opening a pull request

- Use only synthetic data and fixture tools.
- Do not commit credentials, customer content, proprietary prompts, or third-party attack payloads without redistribution rights.
- Add paired clean/adversarial tests for new attack operators.
- Include model/provider assumptions, attack budget, expected state predicate, and utility impact.
- Keep Plugin and Agent Skill metadata self-contained and searchable.
- Check keyboard navigation, visible focus, contrast, zoom, and reduced-motion behavior for UI changes.

## Development checks

```bash
python scripts/validate_distribution.py
bash -n install.sh site/install.sh
cd caps_verify && pytest
cd ../caps_app && pytest
```

Report high-severity vulnerabilities privately through GitHub Security Advisories rather than a public issue.
