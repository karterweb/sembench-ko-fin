"""CLI adapter — delegates redact/rehydrate to a subprocess command."""
from __future__ import annotations

import json
import subprocess
from typing import Any, cast

from sembench.adapters.base import PseudonymizationAdapter


class CliAdapter(PseudonymizationAdapter):
    """Calls a CLI tool: <cmd> redact <json_input> → json stdout"""

    def __init__(self, command: list[str], adapter_id_override: str | None = None) -> None:
        self._command = command
        self._adapter_id_override = adapter_id_override

    @property
    def adapter_id(self) -> str:
        return self._adapter_id_override or f"cli-adapter:{' '.join(self._command)}"

    def redact(self, raw_utterance: str, raw_context: dict[str, Any]) -> dict[str, Any]:
        input_data = json.dumps(
            {"utterance": raw_utterance, "context": raw_context}, ensure_ascii=False
        )
        result = subprocess.run(
            [*self._command, "redact"],
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )
        return cast(dict[str, Any], json.loads(result.stdout))

    def rehydrate(self, external_response: str, raw_context: dict[str, Any]) -> str:
        input_data = json.dumps(
            {"response": external_response, "context": raw_context}, ensure_ascii=False
        )
        result = subprocess.run(
            [*self._command, "rehydrate"],
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )
        return str(json.loads(result.stdout))
