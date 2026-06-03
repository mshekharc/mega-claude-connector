TOOL_SPECS = [
    {
        "name": "mega_storage_info",
        "description": "Get Mega.nz storage usage and quota",
        "schema": {"type": "object", "properties": {}},
    },
    {
        "name": "mega_list_files",
        "description": "List files and folders. Optionally filter by folder path.",
        "schema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Remote folder name to list (omit for root)"},
            },
        },
    },
    {
        "name": "mega_search",
        "description": "Search for files or folders by name",
        "schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "mega_upload",
        "description": "Upload a local file to Mega.nz",
        "schema": {
            "type": "object",
            "properties": {
                "local_path": {"type": "string", "description": "Absolute path to the local file"},
                "remote_folder": {"type": "string", "description": "Destination folder name on Mega (omit for root)"},
            },
            "required": ["local_path"],
        },
    },
    {
        "name": "mega_download",
        "description": "Download a file from Mega.nz to a local directory",
        "schema": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string", "description": "Name of the file on Mega"},
                "local_dest": {"type": "string", "description": "Local directory to save to (default: current dir)"},
            },
            "required": ["file_name"],
        },
    },
    {
        "name": "mega_create_folder",
        "description": "Create a new folder on Mega.nz",
        "schema": {
            "type": "object",
            "properties": {
                "folder_name": {"type": "string", "description": "Name of the new folder"},
                "parent_folder": {"type": "string", "description": "Parent folder name (omit for root)"},
            },
            "required": ["folder_name"],
        },
    },
    {
        "name": "mega_delete",
        "description": "Delete a file or folder from Mega.nz",
        "schema": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string", "description": "Name of the file or folder to delete"},
            },
            "required": ["file_name"],
        },
    },
]


def as_anthropic_tools() -> list[dict]:
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["schema"]}
        for t in TOOL_SPECS
    ]


def as_mcp_tools():
    from mcp import types
    return [
        types.Tool(name=t["name"], description=t["description"], inputSchema=t["schema"])
        for t in TOOL_SPECS
    ]
