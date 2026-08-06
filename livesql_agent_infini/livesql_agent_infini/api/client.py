"""HTTP client for InfiniSynapse API calls."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote

import requests

from livesql_agent_infini.config import (
    DEFAULT_API_RETRIES,
    DEFAULT_API_TIMEOUT,
    INFINI_CREDENTIAL_PATH,
)

logger = logging.getLogger("livesql_agent_infini")


def resolve_timeout(timeout: float | None = None) -> float:
    if timeout is not None:
        return timeout
    env_timeout = os.environ.get("INFINI_API_TIMEOUT")
    if env_timeout:
        return float(env_timeout)
    return DEFAULT_API_TIMEOUT


def _load_credential(
    credential_path: str | os.PathLike | None = None,
) -> tuple[str, str, str | None]:
    if credential_path is not None:
        path = Path(credential_path)
    else:
        env_path = os.environ.get("INFINI_CREDENTIAL_PATH")
        path = Path(env_path) if env_path else INFINI_CREDENTIAL_PATH

    with open(path, "r", encoding="utf-8") as f:
        cred = json.load(f)

    api_url = os.environ.get("INFINI_API_URL") or cred["api_url"]
    api_key = os.environ.get("INFINI_API_KEY") or cred["api_key"]
    console_url = os.environ.get("INFINI_CONSOLE_URL") or cred.get("console_url")
    return (
        api_url.rstrip("/"),
        api_key,
        console_url.rstrip("/") if isinstance(console_url, str) and console_url else None,
    )


class InfiniClient:
    """Thin wrapper around requests with base URL and Bearer auth."""

    def __init__(
        self,
        credential_path: str | os.PathLike | None = None,
        timeout: float | None = None,
        use_console: bool = False,
        retries: int | None = None,
    ) -> None:
        api_url, self._api_key, console_url = _load_credential(credential_path)
        if use_console:
            if not console_url:
                raise ValueError(
                    "console_url is not configured in the credential file."
                )
            self.api_url = console_url
        else:
            self.api_url = api_url
        self.timeout = resolve_timeout(timeout)
        env_retries = os.environ.get("INFINI_API_RETRIES")
        self.retries = (
            retries
            if retries is not None
            else int(env_retries) if env_retries else DEFAULT_API_RETRIES
        )

    def _headers(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        if extra:
            headers.update(extra)
        return headers

    def _url(self, path: str, *path_params: str) -> str:
        encoded = "/".join(quote(str(part), safe="") for part in path_params)
        path = path.rstrip("/")
        if encoded:
            path = f"{path}/{encoded}"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.api_url}{path}"

    def request(
        self,
        method: str,
        path: str,
        *path_params: str,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        data: Any = None,
        files: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        raise_for_status: bool = True,
    ) -> requests.Response:
        kwargs: dict[str, Any] = {
            "headers": self._headers(headers),
            "params": params,
            "timeout": resolve_timeout(timeout if timeout is not None else self.timeout),
        }
        if files is not None:
            kwargs["files"] = files
            if data is not None:
                kwargs["data"] = data
        elif data is not None:
            kwargs["data"] = data
        else:
            kwargs["json"] = json_body

        url = self._url(path, *path_params)
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = requests.request(method, url, **kwargs)
                if raise_for_status and resp.status_code >= 400 and resp.status_code != 404:
                    resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                wait_s = min(2 ** (attempt - 1), 8)
                logger.warning(
                    "API request failed (%s %s, attempt %d/%d): %s; retrying in %ss",
                    method,
                    url,
                    attempt,
                    self.retries,
                    exc,
                    wait_s,
                )
                time.sleep(wait_s)

        assert last_error is not None
        raise last_error

    def get(self, path: str, *path_params: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, *path_params, **kwargs)

    def post(self, path: str, *path_params: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, *path_params, **kwargs)


def unwrap(body: Any) -> Any:
    if isinstance(body, dict) and "data" in body:
        return body["data"]
    return body


def ping_api(
    credential_path: str | os.PathLike | None = None,
    timeout: float | None = None,
) -> str:
    """Return the configured API base URL after a lightweight connectivity check."""
    client = InfiniClient(credential_path=credential_path, timeout=timeout)
    client.get("/api/ai_byzer/available", raise_for_status=False)
    return client.api_url
