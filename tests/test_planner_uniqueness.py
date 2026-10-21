# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from __future__ import annotations

import importlib.util
from pathlib import Path
import random
import sys
import types
from types import SimpleNamespace

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components/smart_meal_planner"

custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(ROOT / "custom_components")]
package = types.ModuleType("custom_components.smart_meal_planner")
package.__path__ = [str(PACKAGE_PATH)]
sys.modules["custom_components"] = custom_components
sys.modules["custom_components.smart_meal_planner"] = package

homeassistant = types.ModuleType("homeassistant")
helpers = types.ModuleType("homeassistant.helpers")
aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
aiohttp_client.async_get_clientsession = lambda hass: None
storage = types.ModuleType("homeassistant.helpers.storage")
storage.Store = type("Store", (), {})
update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
update_coordinator.DataUpdateCoordinator = type("DataUpdateCoordinator", (), {})
sys.modules.update(
    {
        "homeassistant": homeassistant,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.aiohttp_client": aiohttp_client,
        "homeassistant.helpers.storage": storage,
        "homeassistant.helpers.update_coordinator": update_coordinator,
    }
)


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(
        f"custom_components.smart_meal_planner.{name}",
        PACKAGE_PATH / f"{name}.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


for dependency in ("const", "security", "recipes", "url_import", "provider"):
    load_module(dependency)
planner_module = load_module("planner")


def make_runtime():
    runtime = object.__new__(planner_module.MealPlannerRuntime)
    runtime.entry = SimpleNamespace(options={})
    runtime.state = {
        "weeks": {},
        "imported_recipes": [],
        "internet_recipes": [],
        "ratings": {},
        "blocked_recipes": [],
        "history": [],
    }
    return runtime


def test_week_suggestions_do_not_repeat_recipe_ids():
    runtime = make_runtime()
    random.seed(42)
    for day_index in range(7):
        runtime.generate_day(day_index)
    week = runtime.get_week(0)
    recipes = [
        recipe
        for day in week["days"]
        for recipe in day.get("suggestions", [])
    ]
    recipe_ids = [recipe["id"] for recipe in recipes]
    recipe_names = [recipe["name"].casefold() for recipe in recipes]
    assert len(recipe_ids) == 21
    assert len(recipe_ids) == len(set(recipe_ids))
    assert len(recipe_names) == len(set(recipe_names))


def test_regenerating_day_avoids_previous_and_other_day_suggestions():
    runtime = make_runtime()
    random.seed(42)
    for day_index in range(7):
        runtime.generate_day(day_index)
    week = runtime.get_week(0)
    previous = {recipe["id"] for recipe in week["days"][0]["suggestions"]}
    other_days = {
        recipe["id"]
        for day in week["days"][1:]
        for recipe in day.get("suggestions", [])
    }

    runtime.generate_day(0)
    regenerated = {recipe["id"] for recipe in week["days"][0]["suggestions"]}

    assert regenerated.isdisjoint(previous)
    assert regenerated.isdisjoint(other_days)


def test_display_drops_unsafe_urls_from_existing_storage():
    runtime = make_runtime()
    recipe = {
        "id": "stored_test",
        "name": "Stored recipe",
        "url": "javascript:alert(1)",
        "youtube": "data:text/html,unsafe",
        "image": "file:///etc/passwd",
    }
    displayed = runtime._recipe_for_display(recipe)
    assert displayed["url"] is None
    assert displayed["youtube"] is None
    assert displayed["image"] is None
