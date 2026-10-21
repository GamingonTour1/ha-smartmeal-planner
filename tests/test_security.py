# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "custom_components/smart_meal_planner/security.py"

spec = importlib.util.spec_from_file_location("smart_meal_planner_security", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
safe_http_url = module.safe_http_url


def test_safe_http_url_accepts_http_and_https():
    assert safe_http_url("https://example.com/recipe") == "https://example.com/recipe"
    assert safe_http_url("http://example.com/video") == "http://example.com/video"


def test_safe_http_url_rejects_unsafe_schemes():
    assert safe_http_url("javascript:alert(1)") is None
    assert safe_http_url("data:text/html,<script>alert(1)</script>") is None
    assert safe_http_url("file:///etc/passwd") is None
    assert safe_http_url("mailto:test@example.com") is None
    assert safe_http_url("//example.com/relative") is None
    assert safe_http_url("not a url") is None
