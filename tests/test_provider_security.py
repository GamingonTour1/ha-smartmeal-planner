# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components/smart_meal_planner"

custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(ROOT / "custom_components")]
package = types.ModuleType("custom_components.smart_meal_planner")
package.__path__ = [str(PACKAGE_PATH)]
sys.modules.setdefault("custom_components", custom_components)
sys.modules.setdefault("custom_components.smart_meal_planner", package)

homeassistant = types.ModuleType("homeassistant")
helpers = types.ModuleType("homeassistant.helpers")
aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
aiohttp_client.async_get_clientsession = lambda hass: None
sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.helpers", helpers)
sys.modules.setdefault("homeassistant.helpers.aiohttp_client", aiohttp_client)

for module_name in ("security", "provider"):
    spec = importlib.util.spec_from_file_location(
        f"custom_components.smart_meal_planner.{module_name}",
        PACKAGE_PATH / f"{module_name}.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

provider_module = sys.modules["custom_components.smart_meal_planner.provider"]


def test_themealdb_normalize_drops_unsafe_external_urls():
    provider = object.__new__(provider_module.TheMealDBProvider)
    recipe = provider._normalize(
        {
            "idMeal": "1",
            "strMeal": "Security Test",
            "strSource": "javascript:alert(1)",
            "strYoutube": "data:text/html,<script>alert(1)</script>",
            "strMealThumb": "file:///etc/passwd",
        }
    )
    assert recipe["url"] is None
    assert recipe["youtube"] is None
    assert recipe["image"] is None


def test_themealdb_normalize_keeps_https_urls():
    provider = object.__new__(provider_module.TheMealDBProvider)
    recipe = provider._normalize(
        {
            "idMeal": "2",
            "strMeal": "Security Test",
            "strSource": "https://example.com/recipe",
            "strYoutube": "https://www.youtube.com/watch?v=test",
            "strMealThumb": "https://example.com/image.jpg",
        }
    )
    assert recipe["url"] == "https://example.com/recipe"
    assert recipe["youtube"] == "https://www.youtube.com/watch?v=test"
    assert recipe["image"] == "https://example.com/image.jpg"
