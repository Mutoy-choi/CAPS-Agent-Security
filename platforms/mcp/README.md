# Generic MCP and API hosts

CAPS Verify can be used independently of any branded agent host.

```bash
cd caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,mcp]"

caps-verify-mcp --state .caps/fixture-state.json
```

Connect the resulting stdio command through the host's MCP configuration. Keep it local and fixture-only. Use `stdio.example.json` as a shape reference, not as an automatically enabled configuration.

For API-based apps, run `caps-verify-runtime` or `caps-verify-gateway` in front of an OpenAI-compatible or supported provider endpoint. Active evaluations remain separate synthetic sessions.
