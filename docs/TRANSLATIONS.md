# README translation guide

CAPS uses English `README.md` as the source of truth and currently maintains these localized entry points:

| Language | File | Locale |
|---|---|---|
| English | `README.md` | `en` |
| Korean | `README.ko.md` | `ko` |
| Japanese | `README.ja.md` | `ja` |
| Simplified Chinese | `README.zh-CN.md` | `zh-CN` |
| Spanish | `README.es.md` | `es` |

## What must remain synchronized

Every README must preserve the same operational meaning for:

- supported platforms and package paths;
- shell and PowerShell installation commands;
- research profiles and optional libraries;
- ASR success criteria and measurement caveats;
- safety boundaries and private vulnerability reporting;
- repository, discovery-site, platform-matrix, and research-documentation links.

Do not translate commands, paths, package names, profile IDs, filenames, or API endpoints.

## Preferred terminology

Use the established English technical term in parentheses when a localized translation could be ambiguous.

| Term | Meaning to preserve |
|---|---|
| synthetic environment | isolated test environment with no live-user or production side effects |
| fixture tool | controlled test tool whose state changes can be measured deterministically |
| prompt injection | untrusted content that attempts to override or redirect agent instructions |
| confused deputy | an agent using legitimate authority on behalf of an unauthorized instruction |
| provenance | evidence of where instructions, artifacts, and tool results originated |
| safety drift | degradation of policy adherence across context, composition, or multiple turns |
| ASR | attack success rate under the stated validity and success conditions |

## Review checklist

- [ ] The language selector links to all maintained README files.
- [ ] The current language is bold and is not linked to itself.
- [ ] Code fences are balanced.
- [ ] Required platform names and shared commands remain present.
- [ ] No live-user bypass claim or universal safety-certification claim was introduced.
- [ ] Security reports still point to the CAPS repository advisory flow.
- [ ] `python scripts/validate_readmes.py` passes.

## Adding another language

1. Copy the English README to `README.<locale>.md`.
2. Translate prose while preserving commands, identifiers, paths, and links.
3. Add the language to every README selector.
4. Add the locale to this document and `scripts/validate_readmes.py`.
5. Request native-speaker technical review.
6. Keep the pull request in draft until the README validation workflow passes.
