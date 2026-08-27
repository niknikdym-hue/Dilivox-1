from __future__ import annotations

import json
import re
from typing import Any, Iterable


REDACTED = "[REDACTED]"
_SENSITIVE_KEYS = re.compile(
    r"(authorization|token|secret|password|api[-_]?key|client[-_]?login|counter[-_]?id|campaign[-_]?id|resource[-_]?id)",
    re.IGNORECASE,
)


def redact(value: Any, secrets: Iterable[str] = ()) -> Any:
    secret_values = tuple(secret for secret in secrets if secret)
    if isinstance(value, dict):
        return {
            key: REDACTED if _SENSITIVE_KEYS.search(str(key)) else redact(item, secret_values)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item, secret_values) for item in value]
    if isinstance(value, str):
        result = value
        for secret in secret_values:
            result = result.replace(secret, REDACTED)
        result = re.sub(r"(?i)(Bearer|OAuth)\s+[A-Za-z0-9._~+/=-]+", rf"\1 {REDACTED}", result)
        return result
    return value


def safe_json(value: Any, secrets: Iterable[str] = ()) -> str:
    return json.dumps(redact(value, secrets), ensure_ascii=False, sort_keys=True)
