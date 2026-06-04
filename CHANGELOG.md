# Changelog

## [0.1.9] - 2026-06-04
### Changed
- CLI now uses claude.ai OAuth token (Pro subscription) automatically if Claude Code is installed, eliminating API credit usage
- Falls back to `ANTHROPIC_API_KEY` / stored key only when no OAuth token is found
- Startup message now shows which auth method is active
### Added
- `get_claude_oauth_token()` in `config.py` — reads `~/.claude/.credentials.json`, handles Linux, Windows, and WSL paths
- `_claude_credentials_path()` — resolves credentials file across environments (WSL checks `/mnt/c/Users/$USER/.claude/`)

## [0.1.8] - 2026-06-04
### Fixed
- Vendored `mega.py` client into `mega_connector/_mega/` — eliminates the `mega.py` PyPI dependency whose pinned `tenacity<6.0.0` constraint made the package uninstallable on Python 3.11+ (tenacity 5.x uses the removed `asyncio.coroutine`)
- Restored `tenacity>=8.0.0` — now unconstrained by the vendored mega client
### Changed
- `requests>=2.28.0` and `pycryptodome>=3.15.0` are now direct dependencies (previously transitive via `mega.py`)

## [0.1.7] - 2026-06-04
### Fixed
- Changed `tenacity>=8.0.0` to `>=5.1.5` to unblock pip install (partial fix — later superseded by v0.1.8 vendoring)
### Changed
- Publish workflow switched from OIDC Trusted Publishing to API token (`PYPI_API_TOKEN` secret) — Trusted Publishing requires a GitHub repo verification step on PyPI that was failing

## [0.1.6] - 2026-06-03
### Fixed
- `@retry` now catches only transient errors (`ConnectionError`, `TimeoutError`, `OSError`, `RequestError`) — previously caught `Exception` which pointlessly retried deterministic failures like `FileNotFoundError` and `ValueError`
- `_with_reauth` now catches `mega.errors.RequestError` specifically (error code -15 = auth expired) instead of fragile string-matching on exception messages

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
- GitHub Actions publish workflow (later changed to API token auth in v0.1.7)

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
