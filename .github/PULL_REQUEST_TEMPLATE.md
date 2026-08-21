## Summary

Describe the user-visible or research-facing change and why it is needed.

## Validation

- [ ] `python scripts/validate_distribution.py`
- [ ] `python scripts/validate_readmes.py`
- [ ] Relevant `pytest` suites
- [ ] Shell or PowerShell syntax checks when installers changed

## Safety and provenance

- [ ] Tests and examples use synthetic data and fixture tools only.
- [ ] No credentials, customer content, production prompts, or destructive side effects are included.
- [ ] New research probes identify their source ideas and do not redistribute restricted datasets.
- [ ] Results are not presented as a universal safety certification.

## Distribution and documentation

- [ ] Canonical `skills/` and platform copies remain synchronized.
- [ ] Platform paths, package versions, and installer commands are updated where needed.
- [ ] Localized READMEs remain synchronized when shared behavior changed.
- [ ] Accessibility was checked for UI or documentation presentation changes.
