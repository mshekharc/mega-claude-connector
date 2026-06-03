import os
from mega import Mega
from .config import get_credentials

_mega = Mega()
_client = None


def _get_client():
    global _client
    if _client is None:
        creds = get_credentials()
        _client = _mega.login(creds["mega_email"], creds["mega_password"])
    return _client


def get_storage_info() -> dict:
    m = _get_client()
    quota = m.get_quota()
    storage = m.get_storage_space()
    return {
        "used_bytes": storage.get("used", 0),
        "total_bytes": storage.get("total", 0),
        "quota_bytes": quota,
    }


def list_files(folder_path: str | None = None) -> list[dict]:
    m = _get_client()
    if folder_path:
        folder = m.find(folder_path)
        if not folder:
            raise ValueError(f"Folder not found: {folder_path}")
        files = m.get_files_in_node(folder[0])
    else:
        files = m.get_files()

    result = []
    for file_id, file_data in files.items():
        attrs = file_data.get("a", {})
        result.append({
            "id": file_id,
            "name": attrs.get("n", "[no name]") if attrs else "[no name]",
            "type": "folder" if file_data.get("t") == 1 else "file",
            "size": file_data.get("s", 0),
        })
    return result


def search_files(query: str) -> list[dict]:
    m = _get_client()
    results = m.find(query)
    if not results:
        return []
    output = []
    for item in results:
        attrs = item.get("a", {})
        output.append({
            "id": item.get("h"),
            "name": attrs.get("n", "[no name]") if attrs else "[no name]",
            "type": "folder" if item.get("t") == 1 else "file",
            "size": item.get("s", 0),
        })
    return output


def upload_file(local_path: str, remote_folder: str | None = None) -> dict:
    m = _get_client()
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    dest = None
    if remote_folder:
        folder = m.find(remote_folder)
        if not folder:
            raise ValueError(f"Remote folder not found: {remote_folder}")
        dest = folder[0]
    file = m.upload(local_path, dest)
    link = m.get_upload_link(file)
    return {"name": os.path.basename(local_path), "link": link}


def download_file(file_name: str, local_dest: str = ".") -> str:
    m = _get_client()
    results = m.find(file_name)
    if not results:
        raise FileNotFoundError(f"File not found on Mega: {file_name}")
    m.download(results[0], local_dest)
    return os.path.join(local_dest, file_name)


def create_folder(folder_name: str, parent_folder: str | None = None) -> dict:
    m = _get_client()
    parent = None
    if parent_folder:
        found = m.find(parent_folder)
        if not found:
            raise ValueError(f"Parent folder not found: {parent_folder}")
        parent = found[0]
    folder = m.create_folder(folder_name, parent)
    return {"name": folder_name, "id": folder.get(folder_name)}


def delete_node(file_name: str) -> bool:
    m = _get_client()
    results = m.find(file_name)
    if not results:
        raise FileNotFoundError(f"Not found: {file_name}")
    m.delete(results[0])
    return True
