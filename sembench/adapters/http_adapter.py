"""HTTP adapter — delegates redact/rehydrate to a REST service."""
from __future__ import annotations

from typing import Any

import httpx

from sembench.adapters.base import PseudonymizationAdapter


class HttpAdapter(PseudonymizationAdapter):
    """Calls a REST service: POST /redact → {payload}, POST /rehydrate → {response}"""

    def __init__(self, base_url: str, adapter_id_override: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._adapter_id_override = adapter_id_override
        self._client = httpx.Client()

    @property
    def adapter_id(self) -> str:
        return self._adapter_id_override or f"http-adapter:{self._base_url}"

    def redact(self, raw_utterance: str, raw_context: dict[str, Any]) -> dict[str, Any]:
        resp = self._client.post(
            f"{self._base_url}/redact",
            json={"utterance": raw_utterance, "context": raw_context},
        )
        resp.raise_for_status()
        return resp.json()["payload"]

    def rehydrate(self, external_response: str, raw_context: dict[str, Any]) -> str:
        resp = self._client.post(
            f"{self._base_url}/rehydrate",
            json={"response": external_response, "context": raw_context},
        )
        resp.raise_for_status()
        return resp.json()["result"]
