# mega-claude-connector

Mega.nz MCP server + Claude-powered CLI. Published on PyPI (`pip install mega-claude-connector`).

## Billing rule (important)
Owner is on claude.ai Pro (OAuth). Default credential path is OAuth passthrough from
`~/.claude/.credentials.json` — keep it that way. The API key in `.env` bills separately;
never make it the default, only use for explicit API tests.

## Layout
- `src/mega_connector/cli.py` — streaming chat CLI with tool-use loop
- `src/mega_connector/config.py` — credential chain: env → file → prompt → OAuth
- MCP entry point: `.venv/bin/mega-claude-mcp` (registered in Windows Claude Code
  settings.json via `wsl.exe -d Ubuntu --` wrapper)

## Env
WSL Ubuntu, Python 3.12, per-project `.venv`. Public repo — no real secrets in code;
`.env` is gitignored.
