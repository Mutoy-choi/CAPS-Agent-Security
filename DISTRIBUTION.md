# CAPS Unlock Lab distribution checklist

## Package surfaces

- ChatGPT/Codex: `.codex-plugin/plugin.json`, `skills/`, `agents/openai.yaml`, `.agents/skills/`, `AGENTS.md`.
- Claude Code: `.claude-plugin/marketplace.json`, `plugins/caps-unlock/`.
- Gemini CLI: `gemini-extension.json`, `GEMINI.md`, `commands/caps/`, `skills/`.
- GitHub Copilot: `.github/skills/`, `.github/agents/`, `.github/copilot-instructions.md`.
- Cursor: `.cursor/rules/` and disabled MCP example.
- Cline: `.clinerules/` and workflows.
- Windsurf: `.windsurf/rules/` and workflows.
- OpenCode: `.agents/skills/` and `AGENTS.md`.
- Generic MCP/API: `caps_verify/` and `platforms/mcp/`.

## Automated validation

- All Plugin/extension JSON parses.
- Marketplace and package names/versions are synchronized at `0.8.0`.
- Canonical `skills/` files are byte-identical to distributed copies.
- `agents/openai.yaml`, Gemini commands, Copilot custom agent, IDE rules, and MCP examples exist.
- Unix and Pages installers are identical; PowerShell installers are identical.
- Shell and PowerShell syntax is checked.
- Claude Code Plugin validation runs in CI.
- Legacy ChillMCP paths are rejected.
- Pages canonical URLs, platform page, sitemap, structured data, `skills.json`, `platforms.json`, `llms.txt`, and `llms-full.txt` are checked.

## Public directory steps

1. Merge the release branch to `main`.
2. Enable GitHub Pages through the provided Actions workflow.
3. Create release `v0.8.0`.
4. Test each installer from a clean environment.
5. Submit the ChatGPT/Codex Plugin package to the universal directory when ready.
6. Add repository topic `gemini-cli-extension` and follow the Gemini extension gallery process.
7. Keep Claude Marketplace metadata and published Pages `marketplace.json` synchronized.
8. Submit `sitemap.xml` to search consoles and monitor crawl errors.

## Repository topics

```text
agent-skills
ai-agent-security
chatgpt-plugin
claude-code-plugin
codex
continuous-red-team
gemini-cli-extension
github-copilot
jailbreak-benchmark
llm-security
mcp-security
model-unlock
multimodal-security
prompt-injection
```

Search indexing and directory acceptance are not guaranteed. Do not publish fabricated ratings, reviews, download counts, or safety claims.
