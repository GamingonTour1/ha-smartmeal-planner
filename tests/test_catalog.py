# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Lightweight repository checks that do not require Home Assistant."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_builtin_catalog_size_and_shape():
    recipes = _load_module(
        "smart_meal_planner_recipes",
        ROOT / "custom_components/smart_meal_planner/recipes.py",
    ).BUILTIN_RECIPES
    assert len(recipes) >= 500
    assert len({recipe["id"] for recipe in recipes}) == len(recipes)
    assert all(recipe["ingredients"] for recipe in recipes)
    assert all(recipe["instructions"] for recipe in recipes)


def test_builtin_catalog_has_structured_quantities():
    module = _load_module(
        "smart_meal_planner_recipes_quantities",
        ROOT / "custom_components/smart_meal_planner/recipes.py",
    )
    recipes = module.BUILTIN_RECIPES
    assert all(recipe.get("base_servings") == 2 for recipe in recipes)
    assert all(recipe.get("ingredient_details") for recipe in recipes)
    assert all(
        detail.get("name") and isinstance(detail.get("amount"), (int, float)) and detail.get("unit")
        for recipe in recipes
        for detail in recipe["ingredient_details"]
    )
    assert all(
        any(char.isdigit() for char in line)
        for recipe in recipes
        for line in recipe["ingredients"]
    )


def test_quantity_scaling_for_known_recipe():
    module = _load_module(
        "smart_meal_planner_recipes_scaling",
        ROOT / "custom_components/smart_meal_planner/recipes.py",
    )
    recipe = next(recipe for recipe in module.BUILTIN_RECIPES if recipe["name"] == "Eintopf mit Ei – Pesto")
    doubled = [module.format_ingredient_detail(detail, 2) for detail in recipe["ingredient_details"]]
    assert "800 g Kartoffeln" in doubled
    assert "200 g Pesto" in doubled
    assert "8 Eier" in doubled
