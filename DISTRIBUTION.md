# CAPS Distribution Checklist

## Public endpoints

- Repository: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Pages: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Marketplace: `https://mutoy-choi.github.io/CAPS-Agent-Security/marketplace.json`
- Skills registry: `https://mutoy-choi.github.io/CAPS-Agent-Security/skills.json`
- Installer: `https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh`

## Release checklist

1. Run all GitHub Actions workflows.
2. Validate the Claude Code Marketplace and Plugin:

   ```bash
   claude plugin validate .
   ```

3. Validate Agent Skills with the current reference validator when available.
4. Test from a clean user account:

   ```bash
   claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
   claude plugin install caps-security@caps-labs --scope user
   curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
   ```

5. Enable GitHub Pages using GitHub Actions.
6. Create a signed release and update all component versions together.
7. Submit `sitemap.xml` to search consoles.
8. Confirm keyboard navigation, visible focus, 200% zoom, reduced motion, and screen-reader labels.

## Suggested repository metadata

Description:

`Authorized LLM unlock research, Claude Code Plugin, Agent Skills, MCP security, prompt-injection and jailbreak ASR evaluation.`

Topics:

```text
agent-skills
ai-agent-security
claude-code-plugin
continuous-red-team
jailbreak-benchmark
llm-security
mcp-security
model-unlock
multimodal-security
prompt-injection
security-testing
```

Search indexing and rich results are not guaranteed. Do not publish fabricated ratings, download counts, benchmark claims, or safety certifications.
