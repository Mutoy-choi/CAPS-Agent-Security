# CAPS Unlock Lab — platform matrix

CAPS keeps one canonical workflow in `skills/` and exposes thin adapters for each host. No adapter starts active attacks or telemetry by itself.

## ChatGPT and Codex

Native files:

```text
.codex-plugin/plugin.json
skills/*/SKILL.md
skills/*/agents/openai.yaml
.agents/skills/
AGENTS.md
.codex/config.toml.example
```

Local Skill installation:

```bash
./install.sh codex
```

Use `$caps-agent-security` or `/skills` in Codex. The repository is also shaped as a skills-only universal Plugin package for local testing and directory submission.

## Claude Code

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

Native files:

```text
.claude-plugin/marketplace.json
plugins/caps-unlock/.claude-plugin/plugin.json
plugins/caps-unlock/skills/
```

## Gemini CLI

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

Native files:

```text
gemini-extension.json
GEMINI.md
commands/caps/*.toml
skills/
```

Commands: `/caps:audit` and `/caps:install`.

## GitHub Copilot

Project install:

```bash
CAPS_SCOPE=project ./install.sh copilot
```

Native files:

```text
.github/skills/
.github/agents/caps-unlock.md
.github/copilot-instructions.md
```

The same Skill directories can be supplied to the Copilot SDK.

## Cursor

From the target project root:

```bash
./install.sh cursor
```

Adds `.cursor/rules/caps-unlock.mdc` and a disabled MCP example. It does not replace existing Cursor rules or enable a server.

## Cline

```bash
./install.sh cline
```

Adds `.clinerules/caps-unlock.md` and `.clinerules/workflows/caps-unlock-audit.md`.

## Windsurf

```bash
./install.sh windsurf
```

Adds `.windsurf/rules/caps-unlock.md` and `.windsurf/workflows/caps-unlock-audit.md`.

## OpenCode

```bash
./install.sh opencode
```

User scope installs to `~/.config/opencode/skills`; project scope uses `.agents/skills`. `AGENTS.md` documents the repository workflow.

## Generic Agent Skills host

```bash
./install.sh skill
```

Copies the two Skill packages to common user locations without starting services.

## Generic MCP or API agent

```bash
./install.sh verify
```

Then use `caps-verify-runtime`, `caps-verify-gateway`, or `caps-verify-mcp`. Example MCP configuration lives in `platforms/mcp/`.

## Windows

Use `install.ps1` with the same mode names.

```powershell
./install.ps1 codex
./install.ps1 gemini
./install.ps1 cursor
```

For remote use, review the script first, then run:

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) codex
```
