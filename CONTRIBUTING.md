# Contributing to CAPS Unlock Lab

CAPS welcomes reproducible benchmarks, fixture environments, defensive controls, accessibility improvements, provider adapters, documentation, and native-speaker translation reviews.

## Before opening a pull request

- Use only synthetic data and fixture tools.
- Do not commit credentials, customer content, proprietary prompts, or third-party attack payloads without redistribution rights.
- Add paired clean/adversarial tests for new attack operators.
- Include model/provider assumptions, attack budget, expected state predicate, and utility impact.
- Keep Plugin and Agent Skill metadata self-contained and searchable.
- Check keyboard navigation, visible focus, contrast, zoom, and reduced-motion behavior for UI changes.
- Keep installation commands, repository URLs, platform rows, and safety language synchronized across localized READMEs.

## Translation changes

English `README.md` is the source of truth. Follow [`docs/TRANSLATIONS.md`](docs/TRANSLATIONS.md) when updating a localized README or adding a language. Run the translation validator before submitting:

```bash
python scripts/validate_readmes.py
```

Machine-assisted translations are welcome when they are clearly reviewed for technical meaning. Native-speaker review is especially valuable for security terms such as indirect prompt injection, confused deputy, fixture, provenance, and safety drift.

## Development checks

```bash
python scripts/validate_distribution.py
python scripts/validate_readmes.py
bash -n install.sh site/install.sh
cd caps_verify && pytest
cd ../caps_app && pytest
```

Report high-severity vulnerabilities privately through GitHub Security Advisories rather than a public issue.
