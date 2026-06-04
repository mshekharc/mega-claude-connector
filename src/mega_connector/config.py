import os
import json
import time
import configparser
import getpass
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "mega-claude-connector"
_CONFIG_FILE = _CONFIG_DIR / "config"

# Credentials are stored in plaintext at _CONFIG_FILE with mode 0o600 (owner read/write only).
# Users who require stronger protection should use env vars or a secrets manager instead.


def _load_file_config() -> dict:
    if not _CONFIG_FILE.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(_CONFIG_FILE)
    return dict(parser["credentials"]) if parser.has_section("credentials") else {}


def _save_config(values: dict):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["credentials"] = values
    with open(_CONFIG_FILE, "w") as f:
        parser.write(f)
    _CONFIG_FILE.chmod(0o600)


def _prompt_and_save(require_anthropic: bool = False) -> dict:
    print("\nFirst-time setup — credentials stored at ~/.config/mega-claude-connector/config (mode 600)\n")
    values = {
        "mega_email": input("Mega.nz email: ").strip(),
        "mega_password": getpass.getpass("Mega.nz password: ").strip(),
    }
    if require_anthropic:
        values["anthropic_api_key"] = getpass.getpass("Anthropic API key: ").strip()
    _save_config(values)
    print(f"\nCredentials saved to {_CONFIG_FILE}\n")
    return values


def _claude_credentials_path() -> Path | None:
    """Find .credentials.json across Linux, Windows, and WSL environments."""
    candidates = [Path.home() / ".claude" / ".credentials.json"]

    # In WSL, Claude Code stores credentials in the Windows home, not Linux home
    try:
        wsl = Path("/proc/version").read_text().lower()
        if "microsoft" in wsl or "wsl" in wsl:
            win_user = os.environ.get("USER", "")
            win_path = Path(f"/mnt/c/Users/{win_user}/.claude/.credentials.json")
            candidates.append(win_path)
    except Exception:
        pass

    return next((p for p in candidates if p.exists()), None)


def get_claude_oauth_token() -> str | None:
    """Return the claude.ai OAuth access token if Claude Code is installed and logged in.

    Using this token routes inference through the user's claude.ai Pro subscription
    instead of billing API credits.
    """
    creds_path = _claude_credentials_path()
    if not creds_path:
        return None
    try:
        data = json.loads(creds_path.read_text())
        oauth = data.get("claudeAiOauth", {})
        expires_at = oauth.get("expiresAt", 0)
        if expires_at and expires_at > time.time() * 1000:
            return oauth.get("accessToken")
    except Exception:
        pass
    return None


def get_credentials(require_anthropic: bool = False) -> dict:
    """Return credentials: env vars → config file → interactive prompt.

    Env vars (MEGA_EMAIL, MEGA_PASSWORD, ANTHROPIC_API_KEY) always take
    precedence and are never written to disk.
    """
    mega_email = os.environ.get("MEGA_EMAIL")
    mega_password = os.environ.get("MEGA_PASSWORD")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if mega_email and mega_password:
        creds: dict = {"mega_email": mega_email, "mega_password": mega_password}
        if anthropic_key:
            creds["anthropic_api_key"] = anthropic_key
        elif require_anthropic:
            # Env vars set for Mega but not for Anthropic — prompt only for that
            creds["anthropic_api_key"] = getpass.getpass("Anthropic API key: ").strip()
        return creds

    file_creds = _load_file_config()
    if file_creds.get("mega_email") and file_creds.get("mega_password"):
        if require_anthropic and not file_creds.get("anthropic_api_key"):
            key = getpass.getpass("Anthropic API key (not yet saved): ").strip()
            file_creds["anthropic_api_key"] = key
            _save_config(file_creds)
        return file_creds

    return _prompt_and_save(require_anthropic=require_anthropic)
