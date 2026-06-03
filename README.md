# mega-claude-connector

A Mega.nz MCP server and Claude-powered CLI for managing your cloud storage with AI.

## Features

- **MCP server** — plug directly into Claude Code or Claude.ai so Claude can browse, upload, download, search, and manage your Mega.nz files as tools
- **CLI** — interactive chat interface powered by Claude for natural-language file management

## Installation

```bash
pip install mega-claude-connector
```

## Setup

Credentials are stored **locally on your machine** at `~/.config/mega-claude-connector/config` and are never included in this package.

On first run you will be prompted:

```
First-time setup — credentials stored only in ~/.config/mega-claude-connector/config

Mega.nz email: your@email.com
Mega.nz password: ••••••••
Anthropic API key: sk-ant-...   # only needed for the CLI, not the MCP server
```

Or set environment variables instead:

```bash
export MEGA_EMAIL=your@email.com
export MEGA_PASSWORD=yourpassword
export ANTHROPIC_API_KEY=sk-ant-...   # CLI only
```

## Usage

### CLI

```bash
mega-claude
```

Example prompts:
- `list all my files`
- `show storage usage`
- `search for invoices`
- `upload /home/user/report.pdf`
- `create a folder called Backups`
- `download photo.jpg to /tmp`

### MCP Server

```bash
mega-claude-mcp
```

Add to your Claude Code MCP config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "mega": {
      "command": "mega-claude-mcp",
      "env": {
        "MEGA_EMAIL": "your@email.com",
        "MEGA_PASSWORD": "yourpassword"
      }
    }
  }
}
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `mega_storage_info` | Get storage usage and quota |
| `mega_list_files` | List files and folders |
| `mega_search` | Search by name |
| `mega_upload` | Upload a local file |
| `mega_download` | Download a file |
| `mega_create_folder` | Create a folder |
| `mega_delete` | Delete a file or folder |

## Requirements

- Python 3.11+
- Mega.nz account
- Anthropic API key (CLI only)

## License

MIT
