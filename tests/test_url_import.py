# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Tests for schema.org recipe import."""
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

security_spec = importlib.util.spec_from_file_location(
    "custom_components.smart_meal_planner.security",
    PACKAGE_PATH / "security.py",
)
security_module = importlib.util.module_from_spec(security_spec)
assert security_spec.loader is not None
sys.modules[security_spec.name] = security_module
security_spec.loader.exec_module(security_module)

spec = importlib.util.spec_from_file_location(
    "custom_components.smart_meal_planner.url_import",
    PACKAGE_PATH / "url_import.py",
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_recipe_json_ld_import():
    html = '''
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Recipe",
      "name": "Test Pasta",
      "image": "/images/pasta.jpg",
      "totalTime": "PT30M",
      "recipeYield": "2 servings",
      "recipeIngredient": ["200 g pasta", "1 tomato"],
      "recipeInstructions": [
        {"@type": "HowToStep", "text": "Cook pasta."},
        {"@type": "HowToStep", "text": "Add tomato."}
      ]
    }
    </script>
    '''
    recipe = module.extract_recipe(html, "https://example.invalid/test")
    assert recipe is not None
    assert recipe["name"] == "Test Pasta"
    assert recipe["minutes"] == 30
    assert recipe["instructions"] == ["Cook pasta.", "Add tomato."]
    assert recipe["url"] == "https://example.invalid/test"
    assert recipe["image"] == "https://example.invalid/images/pasta.jpg"


def test_recipe_import_rejects_unsafe_source_url():
    html = '<script type="application/ld+json">{"@type":"Recipe","name":"Unsafe"}</script>'
    assert module.extract_recipe(html, "javascript:alert(1)") is None


def test_recipe_import_drops_unsafe_image_url():
    html = '''
    <script type="application/ld+json">
    {
      "@type": "Recipe",
      "name": "Unsafe image",
      "image": "javascript:alert(1)",
      "recipeIngredient": []
    }
    </script>
    '''
    recipe = module.extract_recipe(html, "https://example.invalid/test")
    assert recipe is not None
    assert recipe["image"] is None
