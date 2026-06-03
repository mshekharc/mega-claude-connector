import json
import click
import anthropic
from . import mega_client as mc
from .config import get_credentials
from .tools import as_anthropic_tools

SYSTEM = (
    "You are a helpful assistant for managing Mega.nz cloud storage. "
    "Use the provided tools to list, search, upload, download, create folders, and delete files."
)

_DISPATCH = {
    "mega_storage_info":  lambda a: mc.get_storage_info(),
    "mega_list_files":    lambda a: mc.list_files(a.get("folder_path")),
    "mega_search":        lambda a: mc.search_files(a["query"]),
    "mega_upload":        lambda a: mc.upload_file(a["local_path"], a.get("remote_folder")),
    "mega_download":      lambda a: mc.download_file(a["file_name"], a.get("local_dest", ".")),
    "mega_create_folder": lambda a: mc.create_folder(a["folder_name"], a.get("parent_folder")),
    "mega_delete":        lambda a: _confirmed_delete(a["file_name"]),
}


def _confirmed_delete(file_name: str):
    if not click.confirm(f"Delete '{file_name}' from Mega.nz? This cannot be undone"):
        return {"cancelled": True}
    return mc.delete_node(file_name)


def _run_tool(name: str, args: dict):
    try:
        return _DISPATCH[name](args)
    except Exception as e:
        return {"error": str(e)}


@click.command()
@click.option("--model", default="claude-sonnet-4-6", show_default=True,
              envvar="MEGA_CLAUDE_MODEL", help="Anthropic model to use")
def chat(model: str):
    """Interactive Claude-powered Mega.nz file manager."""
    creds = get_credentials(require_anthropic=True)
    client = anthropic.Anthropic(api_key=creds["anthropic_api_key"])
    tools = as_anthropic_tools()
    messages = []

    click.echo("Mega.nz Claude Connector — type 'exit' to quit\n")

    while True:
        user_input = click.prompt("You").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            assistant_text = ""
            tool_uses = []

            with client.messages.stream(
                model=model,
                max_tokens=4096,
                system=SYSTEM,
                tools=tools,
                messages=messages,
            ) as stream:
                for event in stream:
                    if hasattr(event, "type"):
                        if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                            chunk = event.delta.text
                            print(chunk, end="", flush=True)
                            assistant_text += chunk

                final = stream.get_final_message()

            print()
            messages.append({"role": "assistant", "content": final.content})

            if final.stop_reason == "tool_use":
                tool_results = []
                for block in final.content:
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
                break


if __name__ == "__main__":
    chat()
