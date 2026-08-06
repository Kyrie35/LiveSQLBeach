"""InfiniSynapse database registration helpers."""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from typing import Any

from livesql_agent_infini.api.client import InfiniClient, resolve_timeout, unwrap


def normalize_database_name(name: str) -> str:
    """Normalize a string for InfiniSynapse data source lookup."""
    return name.lower().replace("-", "_")


def get_database_by_name(
    database_name: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any] | None:
    """Return the database record for ``database_name``, or ``None`` if missing."""
    database_name = normalize_database_name(database_name)
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get(
        "/api/ai_database/getDatabaseByName",
        database_name,
        raise_for_status=False,
    )
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        resp.raise_for_status()

    try:
        data = unwrap(resp.json())
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    if not (data.get("name") or data.get("id")):
        return None
    return data


def check_database_exists(
    database_name: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> bool:
    return get_database_by_name(
        database_name,
        credential_path=credential_path,
        timeout=timeout,
    ) is not None


def create_upload_directory(
    directory_name: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.post(
        "/api/tools/createDirectory",
        json_body={"directoryName": directory_name},
        raise_for_status=False,
    )
    if resp.status_code == 400 and "already exists" in resp.text.lower():
        return {"directoryPath": directory_name, "message": "already exists"}
    if resp.status_code >= 400:
        resp.raise_for_status()
    return unwrap(resp.json())


def upload_file_to_directory(
    directory: str,
    file_path: str | os.PathLike,
    credential_path: str | os.PathLike | None = None,
    timeout: float = 600.0,
) -> str:
    fp = Path(file_path)
    if not fp.is_file():
        raise FileNotFoundError(f"upload file not found: {fp}")

    mime, _ = mimetypes.guess_type(fp.name)
    mime = mime or "application/octet-stream"

    client = InfiniClient(credential_path=credential_path, timeout=timeout)
    with open(fp, "rb") as fh:
        files = {"file": (fp.name, fh, mime)}
        resp = client.post("/api/tools/upload", directory, files=files)
    payload = unwrap(resp.json())
    if not isinstance(payload, dict) or not payload.get("filename"):
        raise RuntimeError(
            f"upload to {directory!r} returned unexpected payload: {payload!r}"
        )
    return str(payload["filename"])


def add_sqlite_database(
    database_name: str,
    sqlite_path: str,
    nickname: str | None = None,
    description: str | None = None,
    enabled: int = 1,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    config = {"sqlite_path": sqlite_path}
    payload: dict[str, Any] = {
        "name": database_name,
        "nickname": nickname or database_name,
        "description": description if description is not None else database_name,
        "type": "sqlite",
        "enabled": enabled,
        "config": json.dumps(config, ensure_ascii=False),
    }

    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.post("/api/ai_database/add", json_body=payload)
    return unwrap(resp.json())


def delete_database(
    database_name: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any] | None:
    database_name = normalize_database_name(database_name)
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get(
        "/api/ai_database/getDatabaseByName",
        database_name,
        raise_for_status=False,
    )
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        resp.raise_for_status()

    data = unwrap(resp.json())
    if not isinstance(data, dict) or not data.get("id"):
        return None

    del_resp = client.post(
        "/api/ai_database/delete",
        json_body={"ids": [data["id"]]},
    )
    try:
        return unwrap(del_resp.json())
    except ValueError:
        return {"status_code": del_resp.status_code}


def list_databases(
    name: str | None = None,
    type: str | None = None,
    enabled: int | None = None,
    source: str = "all",
    page: int = 1,
    page_size: int = 10000,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "page": page,
        "pageSize": page_size,
        "source": source,
    }
    if name is not None:
        params["name"] = name
    if type is not None:
        params["type"] = type
    if enabled is not None:
        params["enabled"] = enabled

    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get("/api/ai_database/list", params=params)
    data = unwrap(resp.json())
    if isinstance(data, dict) and "items" in data:
        return list(data["items"] or [])
    if isinstance(data, list):
        return data
    return []


def select_databases_by_livesql_db_id(
    db_id: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Match LiveSQLBench ``selected_database`` to registered InfiniSynapse sources."""
    from livesql_agent_infini.config import DATABASE_NAME_PREFIX

    target_name = normalize_database_name(f"{DATABASE_NAME_PREFIX}{db_id}")
    record = get_database_by_name(
        target_name,
        credential_path=credential_path,
        timeout=timeout,
    )
    return [record] if record else []
