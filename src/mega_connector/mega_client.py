import os
from mega import Mega
from mega.errors import RequestError
from tenacity import retry, wait_exponential, retry_if_exception_type, stop_after_attempt
from .config import get_credentials

_mega = Mega()
_client = None

# Only retry transient network/API errors — not deterministic failures like
# FileNotFoundError or ValueError which will never succeed on retry.
_TRANSIENT = (ConnectionError, TimeoutError, OSError, RequestError)


def _login():
    global _client
    creds = get_credentials()
    _client = _mega.login(creds["mega_email"], creds["mega_password"])
    return _client


def _get_client():
    global _client
    if _client is None:
        _login()
    return _client


def _with_reauth(fn, *args, **kwargs):
    """Call fn; on Mega auth failure (RequestError -15), re-login once and retry."""
    try:
        return fn(*args, **kwargs)
    except RequestError as e:
        # Mega API error -15 = EACCESS (auth expired / invalid session)
        if getattr(e, "code", None) == -15 or "-15" in str(e):
            _login()
            return fn(*args, **kwargs)
        raise


@retry(wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type(_TRANSIENT),
       stop=stop_after_attempt(3))
def get_storage_info() -> dict:
    m = _get_client()
    quota = _with_reauth(m.get_quota)
    storage = _with_reauth(m.get_storage_space)
    return {
        "used_bytes": storage.get("used", 0),
        "total_bytes": storage.get("total", 0),
        "quota_bytes": quota,
    }


def list_files(folder_path: str | None = None) -> list[dict]:
    m = _get_client()
    if folder_path:
        folder = _with_reauth(m.find, folder_path)
        if not folder:
            raise ValueError(f"Folder not found: {folder_path}")
        files = _with_reauth(m.get_files_in_node, folder[0])
    else:
        files = _with_reauth(m.get_files)

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
    results = _with_reauth(m.find, query)
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


@retry(wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type(_TRANSIENT),
       stop=stop_after_attempt(3))
def upload_file(local_path: str, remote_folder: str | None = None) -> dict:
    m = _get_client()
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    dest = None
    if remote_folder:
        folder = _with_reauth(m.find, remote_folder)
        if not folder:
            raise ValueError(f"Remote folder not found: {remote_folder}")
        dest = folder[0]
    file = _with_reauth(m.upload, local_path, dest)
    link = m.get_upload_link(file)
    return {"name": os.path.basename(local_path), "link": link}


def download_file(file_name: str, local_dest: str = ".") -> str:
    m = _get_client()
    results = _with_reauth(m.find, file_name)
    if not results:
        raise FileNotFoundError(f"File not found on Mega: {file_name}")
    _with_reauth(m.download, results[0], local_dest)
    return os.path.join(local_dest, file_name)


def create_folder(folder_name: str, parent_folder: str | None = None) -> dict:
    m = _get_client()
    parent = None
    if parent_folder:
        found = _with_reauth(m.find, parent_folder)
        if not found:
            raise ValueError(f"Parent folder not found: {parent_folder}")
        parent = found[0]
    folder = _with_reauth(m.create_folder, folder_name, parent)
    folder_id = next(iter(folder.values()), None)
    return {"name": folder_name, "id": folder_id}


def delete_node(file_name: str) -> bool:
    m = _get_client()
    results = _with_reauth(m.find, file_name)
    if not results:
        raise FileNotFoundError(f"Not found: {file_name}")
    _with_reauth(m.delete, results[0])
    return True
