# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Security helpers for external recipe data."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

_ALLOWED_HTTP_SCHEMES = {"http", "https"}


def safe_http_url(value: Any) -> str | None:
    """Return an HTTP(S) URL or None for unsupported or malformed values."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate:
        return None
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return None
    if parsed.scheme.casefold() not in _ALLOWED_HTTP_SCHEMES or not parsed.netloc:
        return None
    return candidate
