# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Tests for schema.org recipe import."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]

spec = importlib.util.spec_from_file_location(
    "smart_meal_planner_url_import",
    ROOT / "custom_components/smart_meal_planner/url_import.py",
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_recipe_json_ld_import():
    html = '''
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Recipe",
      "name": "Test Pasta",
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
