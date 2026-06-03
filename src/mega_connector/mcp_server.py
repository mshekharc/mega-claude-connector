import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from . import mega_client as mc
from .tools import as_mcp_tools

app = Server("mega-connector")

_DISPATCH = {
    "mega_storage_info": lambda a: mc.get_storage_info(),
    "mega_list_files":   lambda a: mc.list_files(a.get("folder_path")),
    "mega_search":       lambda a: mc.search_files(a["query"]),
    "mega_upload":       lambda a: mc.upload_file(a["local_path"], a.get("remote_folder")),
    "mega_download":     lambda a: mc.download_file(a["file_name"], a.get("local_dest", ".")),
    "mega_create_folder":lambda a: mc.create_folder(a["folder_name"], a.get("parent_folder")),
    # No interactive confirm here — MCP runs non-interactively (no terminal).
    # Delete safety is enforced by Claude's tool-call confirmation in the client UI.
    "mega_delete":       lambda a: mc.delete_node(a["file_name"]),
}

_REQUIRED = {
    "mega_search":        ["query"],
    "mega_upload":        ["local_path"],
    "mega_download":      ["file_name"],
    "mega_create_folder": ["folder_name"],
    "mega_delete":        ["file_name"],
}


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return as_mcp_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name not in _DISPATCH:
            raise ValueError(f"Unknown tool: {name}")

        missing = [k for k in _REQUIRED.get(name, []) if k not in arguments]
        if missing:
            raise ValueError(f"Missing required arguments for {name}: {missing}")

        result = _DISPATCH[name](arguments)
    except Exception as e:
        result = {"error": str(e)}

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main_sync():
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
