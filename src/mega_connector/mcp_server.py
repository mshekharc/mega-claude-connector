import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from . import mega_client as mc

app = Server("mega-connector")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="mega_storage_info",
            description="Get Mega.nz storage usage and quota",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="mega_list_files",
            description="List files and folders. Optionally filter by folder path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string", "description": "Remote folder name to list (omit for root)"},
                },
            },
        ),
        types.Tool(
            name="mega_search",
            description="Search for files or folders by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="mega_upload",
            description="Upload a local file to Mega.nz",
            inputSchema={
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "Absolute path to the local file"},
                    "remote_folder": {"type": "string", "description": "Destination folder name on Mega (omit for root)"},
                },
                "required": ["local_path"],
            },
        ),
        types.Tool(
            name="mega_download",
            description="Download a file from Mega.nz to a local directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "Name of the file on Mega"},
                    "local_dest": {"type": "string", "description": "Local directory to save to (default: current dir)"},
                },
                "required": ["file_name"],
            },
        ),
        types.Tool(
            name="mega_create_folder",
            description="Create a new folder on Mega.nz",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the new folder"},
                    "parent_folder": {"type": "string", "description": "Parent folder name (omit for root)"},
                },
                "required": ["folder_name"],
            },
        ),
        types.Tool(
            name="mega_delete",
            description="Delete a file or folder from Mega.nz",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "Name of the file or folder to delete"},
                },
                "required": ["file_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "mega_storage_info":
            result = mc.get_storage_info()
        elif name == "mega_list_files":
            result = mc.list_files(arguments.get("folder_path"))
        elif name == "mega_search":
            result = mc.search_files(arguments["query"])
        elif name == "mega_upload":
            result = mc.upload_file(arguments["local_path"], arguments.get("remote_folder"))
        elif name == "mega_download":
            result = mc.download_file(arguments["file_name"], arguments.get("local_dest", "."))
        elif name == "mega_create_folder":
            result = mc.create_folder(arguments["folder_name"], arguments.get("parent_folder"))
        elif name == "mega_delete":
            result = mc.delete_node(arguments["file_name"])
        else:
            result = {"error": f"Unknown tool: {name}"}
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
