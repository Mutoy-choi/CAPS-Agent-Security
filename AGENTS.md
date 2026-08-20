# CAPS Unlock Lab — agent instructions

CAPS Unlock Lab is a platform-neutral toolkit for **authorized model-restriction-bypass research** and AI-agent security evaluation.

## Supported hosts

- ChatGPT and Codex plugins or Agent Skills
- Claude Code plugins and Skills
- Gemini CLI extensions and Agent Skills
- GitHub Copilot custom agents and Skills
- Cursor, Cline, Windsurf, and OpenCode project instructions
- Any MCP-capable or OpenAI-compatible host through CAPS Verify

## Repository rules

1. Treat `skills/` as the canonical Skill source. Platform copies must remain semantically identical.
2. Keep active jailbreak probes in isolated synthetic sessions with fixture tools.
3. Never append hidden attack text to a live user's query.
4. Never use real credentials, customer data, payments, external writes, or destructive production tools in evaluation fixtures.
5. Do not enable telemetry, research contribution, public listening addresses, or provider credentials implicitly.
6. Distinguish synthetic benchmark ASR from claims about a production system.

## Validation

After changing CAPS Verify:

```bash
cd caps_verify
python -m pip install -e ".[dev,gateway]"
ruff check src tests
pytest
```

After changing CAPS Research Chat:

```bash
cd caps_app
python -m pip install -e ".[dev]"
ruff check src tests
pytest
```

After changing distribution files:

```bash
python scripts/validate_distribution.py
bash -n install.sh site/install.sh
```

## Output standard

Security reports should include the target model snapshot, host, instruction files, installed extensions, MCP tools and permissions, modality pipeline, defense stack, attack-pack version, query/tool budget, valid and excluded runs, ASR with uncertainty, benign utility, and evidence hashes.
