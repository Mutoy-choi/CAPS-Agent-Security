# CAPS Distribution and Search Checklist

## Already implemented

- Root Claude Code Marketplace catalog: `.claude-plugin/marketplace.json`
- Self-contained installable Plugin: `plugins/caps-security/`
- Cross-client Agent Skills: `.agents/skills/`
- User and project scope installer: `install.sh`
- GitHub Pages discovery site: `site/`
- Pages-hosted Marketplace JSON with `git-subdir` source
- `robots.txt`, `sitemap.xml`, canonical URLs, Open Graph, JSON-LD, `llms.txt`
- `CITATION.cff` and `codemeta.json`
- Distribution validation workflow

## Required before public discovery

1. Merge the Draft PR to `main`.
2. Make this repository public, or copy the marketplace, plugin, Skills, installer and site into a dedicated public distribution repository.
3. Enable **Settings → Pages → Source: GitHub Actions**.
4. Set repository description to:

   `Claude Code plugin + Agent Skills marketplace for MCP, prompt injection, multimodal attachment and LLM jailbreak security evaluation.`

5. Set repository homepage to `https://mutoy-choi.github.io/ChillMCP/`.
6. Add GitHub topics:

   ```text
   ai-agent-security
   agent-skills
   claude-code-plugin
   continuous-red-team
   jailbreak-benchmark
   llm-security
   mcp-security
   multimodal-security
   prompt-injection
   security-testing
   ```

7. Create a GitHub release such as `v0.6.0` and bump Plugin and Marketplace versions on every release.
8. Verify installation from a clean machine:

   ```bash
   claude plugin marketplace add Mutoy-choi/ChillMCP
   claude plugin install caps-security@caps-labs
   curl -fsSL https://mutoy-choi.github.io/ChillMCP/install.sh | bash -s -- skill
   ```

9. Validate with Claude Code:

   ```bash
   claude plugin validate .
   ```

10. Validate Agent Skills with the official reference tool:

   ```bash
   skills-ref validate .agents/skills/caps-agent-security
   skills-ref validate .agents/skills/caps-install
   ```

11. Add the Pages property to Google Search Console and submit:

   `https://mutoy-choi.github.io/ChillMCP/sitemap.xml`

12. Submit the Plugin to Anthropic's official marketplace through the current Claude.ai or Console submission form after public testing.

## Search-content policy

Use accurate visible descriptions. Do not add fake ratings, reviews, downloads, or security claims to structured data. Search indexing and rich results are never guaranteed.
