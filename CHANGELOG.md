# Changelog

## [0.1.5] - 2026-06-03
### Changed
- Upgraded `tenacity` from pinned `==5.1.5` to `>=8.0.0` — mega.py works fine with tenacity 9.x despite its outdated declared constraint
- Removed `__init__.py` asyncio shim — no longer needed with tenacity 8+
### Fixed
- `config.py` env var path now prompts for Anthropic key if Mega env vars are set but `ANTHROPIC_API_KEY` is not
- `config.py` plaintext storage warning added to docstring and comment
### Added
- `py.typed` marker — package now declares PEP 561 typing support
- Comment in `mcp_server.py` explaining intentional no-confirm on delete (MCP is non-interactive)

## [0.1.4] - 2026-06-03
### Fixed
- **Critical:** `list_files()` had corrupted/garbled syntax — was broken on import
- `create_folder()` always returned `id: None` — now uses `next(iter(folder.values()))`
- Stale Mega session no longer silently fails — re-auth triggered automatically on auth errors
### Added
- `tools.py` shared module — tool definitions no longer duplicated between CLI and MCP server
- tenacity `@retry` with exponential backoff on `get_storage_info()` and `upload_file()`
- Hard `click.confirm()` delete confirmation in CLI — no longer relies on Claude's system prompt alone
- Streaming output in CLI via `client.messages.stream()` — responses appear token by token
- Input validation in MCP `call_tool` — missing required args return a clean error instead of `KeyError`
- `--model` now also reads from `MEGA_CLAUDE_MODEL` env var
### Changed
- MCP `call_tool` replaced `if/elif` chain with dispatch dict — consistent with CLI pattern

## [0.1.3] - 2026-06-03
### Fixed
- Runtime shim for tenacity 5.x compatibility on Python 3.11+ (`asyncio.coroutine` removed upstream)
- `requirements.txt` now points to `pyproject.toml` via `-e .` instead of duplicating dependencies
### Added
- GitHub Actions CI workflow (test on Python 3.11 and 3.12)
- GitHub Actions publish workflow using Trusted Publishing (no API tokens needed)

## [0.1.2] - 2026-06-03
### Security
- Password and API key prompts now use `getpass` — input is masked at the terminal

## [0.1.1] - 2026-06-03
### Fixed
- README now included in PyPI package metadata (project description was blank)
- Corrected GitHub homepage URL in `pyproject.toml`

## [0.1.0] - 2026-06-03
### Added
- Initial release
- MCP server with 7 tools: `mega_storage_info`, `mega_list_files`, `mega_search`, `mega_upload`, `mega_download`, `mega_create_folder`, `mega_delete`
- Interactive Claude-powered CLI (`mega-claude`)
- Credential-safe config system: env vars → `~/.config/mega-claude-connector/config` → interactive prompt
