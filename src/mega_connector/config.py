import os
import configparser
import getpass
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "mega-claude-connector"
_CONFIG_FILE = _CONFIG_DIR / "config"


def _load_file_config() -> dict:
    if not _CONFIG_FILE.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(_CONFIG_FILE)
    return dict(parser.get("credentials", {})) if parser.has_section("credentials") else {}


def _save_config(values: dict):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["credentials"] = values
    with open(_CONFIG_FILE, "w") as f:
        parser.write(f)
    _CONFIG_FILE.chmod(0o600)


def _prompt_and_save(require_anthropic: bool = False) -> dict:
    print("\nFirst-time setup — credentials are stored only in ~/.config/mega-claude-connector/config\n")
    values = {
        "mega_email": input("Mega.nz email: ").strip(),
        "mega_password": getpass.getpass("Mega.nz password: ").strip(),
    }
    if require_anthropic:
        values["anthropic_api_key"] = getpass.getpass("Anthropic API key: ").strip()
    _save_config(values)
    print(f"\nCredentials saved to {_CONFIG_FILE}\n")
    return values


def get_credentials(require_anthropic: bool = False) -> dict:
    """Return credentials from env vars → config file → interactive prompt."""
    mega_email = os.environ.get("MEGA_EMAIL")
    mega_password = os.environ.get("MEGA_PASSWORD")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if mega_email and mega_password:
        creds = {"mega_email": mega_email, "mega_password": mega_password}
        if anthropic_key:
            creds["anthropic_api_key"] = anthropic_key
        return creds

    file_creds = _load_file_config()
    if file_creds.get("mega_email") and file_creds.get("mega_password"):
        if require_anthropic and not file_creds.get("anthropic_api_key"):
            key = getpass.getpass("Anthropic API key (not saved yet): ").strip()
            file_creds["anthropic_api_key"] = key
            _save_config(file_creds)
        return file_creds

    return _prompt_and_save(require_anthropic=require_anthropic)
