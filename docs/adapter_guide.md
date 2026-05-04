# Adapter Guide

Implement `PseudonymizationAdapter`:

```python
from sembench.adapters.base import PseudonymizationAdapter

class MyAdapter(PseudonymizationAdapter):
    @property
    def adapter_id(self) -> str:
        return "my-adapter"

    def redact(self, raw_utterance: str, raw_context: dict) -> dict:
        return {"safe_payload": "..."}

    def rehydrate(self, external_response: str, raw_context: dict) -> str:
        return external_response
```

## Safety Contract

`redact()` output is treated as the payload sent to an external LLM. It must not include:

- resident or foreign registration numbers
- card/account/policy numbers
- email or phone numbers
- raw financial institution names when not necessary
- raw hospital names when taxonomy is enough
- exact won amounts when a band or relation is sufficient

## HTTP Contract

HTTP adapters should expose:

- `POST /redact` with `{ "utterance": str, "context": object }`
- `POST /rehydrate` with `{ "response": str, "context": object }`
