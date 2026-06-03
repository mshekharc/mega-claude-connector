import json
import click
import anthropic
from . import mega_client as mc
from .config import get_credentials

TOOLS = [
    {
        "name": "mega_storage_info",
        "description": "Get Mega.nz storage usage and quota",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "mega_list_files",
        "description": "List files and folders. Optionally filter by folder path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Remote folder name (omit for root)"},
            },
        },
    },
    {
        "name": "mega_search",
        "description": "Search for files or folders by name",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "mega_upload",
        "description": "Upload a local file to Mega.nz",
        "input_schema": {
            "type": "object",
            "properties": {
                "local_path": {"type": "string"},
                "remote_folder": {"type": "string"},
            },
            "required": ["local_path"],
        },
    },
    {
        "name": "mega_download",
        "description": "Download a file from Mega.nz",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string"},
                "local_dest": {"type": "string"},
            },
            "required": ["file_name"],
        },
    },
    {
        "name": "mega_create_folder",
        "description": "Create a new folder on Mega.nz",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_name": {"type": "string"},
                "parent_folder": {"type": "string"},
            },
            "required": ["folder_name"],
        },
    },
    {
        "name": "mega_delete",
        "description": "Delete a file or folder from Mega.nz",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string"},
            },
            "required": ["file_name"],
        },
    },
]

SYSTEM = (
    "You are a helpful assistant for managing Mega.nz cloud storage. "
    "Use the provided tools to list, search, upload, download, create folders, and delete files. "
    "Always confirm destructive actions (delete) before proceeding."
)


def _run_tool(name: str, args: dict):
    dispatch = {
        "mega_storage_info": lambda: mc.get_storage_info(),
        "mega_list_files": lambda: mc.list_files(args.get("folder_path")),
        "mega_search": lambda: mc.search_files(args["query"]),
        "mega_upload": lambda: mc.upload_file(args["local_path"], args.get("remote_folder")),
        "mega_download": lambda: mc.download_file(args["file_name"], args.get("local_dest", ".")),
        "mega_create_folder": lambda: mc.create_folder(args["folder_name"], args.get("parent_folder")),
        "mega_delete": lambda: mc.delete_node(args["file_name"]),
    }
    try:
        return dispatch[name]()
    except Exception as e:
        return {"error": str(e)}


@click.command()
@click.option("--model", default="claude-sonnet-4-6", show_default=True)
def chat(model: str):
    """Interactive Claude-powered Mega.nz file manager."""
    creds = get_credentials(require_anthropic=True)
    client = anthropic.Anthropic(api_key=creds["anthropic_api_key"])
    messages = []

    click.echo("Mega.nz Claude Connector — type 'exit' to quit\n")

    while True:
        user_input = click.prompt("You").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages,
            )

            # Collect assistant content
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        click.echo(f"  [tool] {block.name}({json.dumps(block.input)})")
                        result = _run_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                for block in response.content:
                    if hasattr(block, "text"):
                        click.echo(f"\nClaude: {block.text}\n")
                break


if __name__ == "__main__":
    chat()
