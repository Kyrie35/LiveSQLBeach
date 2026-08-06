"""InfiniSynapse task submission and polling helpers."""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any, Iterable, Sequence

import requests

from livesql_agent_infini.api.client import InfiniClient, resolve_timeout, unwrap

logger = logging.getLogger("livesql_agent_infini")


def list_available_engines(
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get("/api/ai_byzer/available")
    data = unwrap(resp.json())
    if isinstance(data, dict) and "items" in data:
        return list(data["items"] or [])
    if isinstance(data, list):
        return data
    return []


def upload_task_file(
    task_id: str,
    file_path: str | os.PathLike,
    subdir: str | None = None,
    naming: str | None = None,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    fp = Path(file_path)
    if not fp.is_file():
        raise FileNotFoundError(f"upload file not found: {fp}")

    params: dict[str, Any] = {}
    if subdir:
        params["subdir"] = subdir
    if naming:
        params["naming"] = naming

    mime, _ = mimetypes.guess_type(fp.name)
    mime = mime or "application/octet-stream"

    client = InfiniClient(
        credential_path=credential_path,
        timeout=max(resolve_timeout(timeout), 120.0),
    )
    with open(fp, "rb") as fh:
        files = {"file": (fp.name, fh, mime)}
        resp = client.post(
            "/api/tools/taskUpload",
            task_id,
            params=params or None,
            files=files,
            timeout=max(resolve_timeout(timeout), 120.0),
        )
    return unwrap(resp.json())


def _build_file_items(
    task_id: str,
    file_paths: Sequence[str | os.PathLike] | None,
    reference_paths: Sequence[str | os.PathLike] | None,
    credential_path: str | os.PathLike | None,
    timeout: float | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def _upload(paths: Iterable[str | os.PathLike], file_type: str, subdir: str | None) -> None:
        for path in paths:
            fp = Path(path)
            uploaded = upload_task_file(
                task_id=task_id,
                file_path=fp,
                subdir=subdir,
                credential_path=credential_path,
                timeout=timeout,
            )
            mime, _ = mimetypes.guess_type(fp.name)
            items.append(
                {
                    "name": uploaded.get("name") or fp.name,
                    "size": int(uploaded.get("size") or fp.stat().st_size),
                    "type": uploaded.get("type") or mime or "application/octet-stream",
                    "logicalPath": uploaded.get("logicalPath"),
                    "assetId": uploaded.get("assetId"),
                    "fileType": file_type,
                }
            )

    if file_paths:
        _upload(file_paths, file_type="data", subdir=None)
    if reference_paths:
        _upload(reference_paths, file_type="reference", subdir="upload_documents")
    return items


def new_task(
    text: str,
    task_id: str | None = None,
    file_paths: Sequence[str | os.PathLike] | None = None,
    reference_paths: Sequence[str | os.PathLike] | None = None,
    files: Sequence[dict[str, Any]] | None = None,
    database_ids: Sequence[str] | None = None,
    engine_id: str | None = None,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    tid = task_id or str(uuid.uuid4())
    file_items: list[dict[str, Any]] = []
    if file_paths or reference_paths:
        file_items.extend(
            _build_file_items(
                task_id=tid,
                file_paths=file_paths,
                reference_paths=reference_paths,
                credential_path=credential_path,
                timeout=timeout,
            )
        )
    if files:
        file_items.extend(files)

    payload: dict[str, Any] = {
        "type": "newTask",
        "taskId": tid,
        "text": text,
        "commandId": str(uuid.uuid4()),
        "clientMessageId": str(uuid.uuid4()),
    }
    if file_items:
        payload["files"] = file_items
    if database_ids:
        payload["databaseIds"] = list(database_ids)
    if engine_id:
        payload["engineId"] = engine_id

    client = InfiniClient(
        credential_path=credential_path,
        timeout=max(resolve_timeout(timeout), 300.0),
    )
    resp = client.post("/api/ai/message", json_body=payload)
    return unwrap(resp.json())


def get_ai_state(
    task_id: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get("/api/ai/state", params={"taskId": task_id})
    return unwrap(resp.json())


def get_task_data(
    task_id: str,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    client = InfiniClient(
        credential_path=credential_path,
        timeout=resolve_timeout(timeout),
    )
    resp = client.get("/api/ai_task/tasks", params={"taskId": task_id})
    return unwrap(resp.json())


def download_task_zip(
    task_id: str,
    dest: str | os.PathLike,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
    chunk_size: int = 256 * 1024,
) -> str:
    client = InfiniClient(
        credential_path=credential_path,
        timeout=max(resolve_timeout(timeout), 600.0),
    )
    url = f"{client.api_url}/api/ai_task/downloadZip"

    dest_path = Path(dest)
    if dest_path.exists() and dest_path.is_dir():
        dest_path = dest_path / f"{task_id}.zip"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(
        url,
        params={"taskId": task_id},
        headers=client._headers(),
        stream=True,
        timeout=max(resolve_timeout(timeout), 600.0),
    ) as resp:
        resp.raise_for_status()
        with open(dest_path, "wb") as handle:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    handle.write(chunk)
    return str(dest_path.resolve())


def _last_non_partial_message(messages: list[dict[str, Any]]) -> dict[str, Any] | None:
    for message in reversed(messages or []):
        if isinstance(message, dict) and not message.get("partial"):
            return message
    return None


def _message_ts(message: dict[str, Any] | None) -> int:
    if not isinstance(message, dict):
        return 0
    try:
        return int(message.get("ts"))
    except (TypeError, ValueError):
        return 0


def _last_non_partial_message_after(
    messages: list[dict[str, Any]],
    *,
    after_ts: int = 0,
    after_index: int = 0,
) -> dict[str, Any] | None:
    window = messages[after_index:] if after_index else messages
    for message in reversed(window or []):
        if not isinstance(message, dict) or message.get("partial"):
            continue
        if after_ts and _message_ts(message) <= after_ts:
            continue
        return message
    return None


def _is_terminal_message(
    message: dict[str, Any] | None,
    *,
    terminal_on_any_ask: bool = True,
) -> bool:
    if not message:
        return False
    mtype = message.get("type")
    if mtype == "say" and message.get("say") == "completion_result":
        return True
    if mtype == "ask":
        ask = message.get("ask")
        if ask == "completion_result":
            return True
        if terminal_on_any_ask and ask not in ("resume_task", "resume_completed_task"):
            return True
    return False


def wait_for_task(
    task_id: str,
    poll_interval: float = 3.0,
    max_wait: float = 1800.0,
    terminal_on_any_ask: bool = True,
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    terminal_status = {"completed", "failed", "cancelled", "canceled", "error"}
    start = time.time()
    seen_alive = False
    poll_failures = 0

    while True:
        elapsed = time.time() - start
        if elapsed > max_wait:
            raise TimeoutError(
                f"wait_for_task({task_id}) exceeded {max_wait}s"
            )

        try:
            data = get_task_data(
                task_id,
                credential_path=credential_path,
                timeout=timeout,
            )
            poll_failures = 0
        except requests.RequestException as exc:
            poll_failures += 1
            logger.warning(
                "wait_for_task(%s): poll failed (#%d): %s",
                task_id,
                poll_failures,
                exc,
            )
            time.sleep(poll_interval)
            continue

        is_running = bool(data.get("isRunning"))
        info = data.get("taskInfo") or {}
        status = str(info.get("status") or "").lower() if isinstance(info, dict) else ""
        messages = data.get("messages") or []

        if is_running or status or messages or info:
            seen_alive = True
        if not seen_alive:
            time.sleep(poll_interval)
            continue

        if status in terminal_status:
            return data
        if _is_terminal_message(
            _last_non_partial_message(messages),
            terminal_on_any_ask=terminal_on_any_ask,
        ):
            return data

        time.sleep(poll_interval)
