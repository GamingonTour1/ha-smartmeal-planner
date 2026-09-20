# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Meal planning engine."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
import random
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_INTERNET_ENABLED,
    CONF_INTERNET_SYNC_DAYS,
    CONF_THEMEALDB_API_KEY,
    DEFAULT_OPTIONS,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .provider import ProviderError, TheMealDBProvider
from .recipes import BUILTIN_RECIPES, format_ingredient_detail
from .url_import import extract_recipe

DAY_NAMES = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
BUILTIN_RECIPE_MAP = {recipe["id"]: recipe for recipe in BUILTIN_RECIPES}


def _csv(value: str) -> list[str]:
    return [item.strip().casefold() for item in (value or "").replace("\n", ",").split(",") if item.strip()]


def monday_of(day: date | None = None) -> date:
    day = day or date.today()
    return day - timedelta(days=day.weekday())


class MealPlannerRuntime:
    """Runtime state and planning logic for one Smart Meal Planner config entry."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.state: dict[str, Any] = {}
        self.coordinator = DataUpdateCoordinator(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="Smart Meal Planner",
        )

    @property
    def options(self) -> dict[str, Any]:
        return {**DEFAULT_OPTIONS, **self.entry.options}

    async def async_load(self) -> None:
        loaded = await self.store.async_load() or {}
        self.state = {
            "weeks": loaded.get("weeks", {}),
            "imported_recipes": loaded.get("imported_recipes", []),
            "internet_recipes": loaded.get("internet_recipes", []),
            "internet_last_sync": loaded.get("internet_last_sync"),
            "ratings": loaded.get("ratings", {}),
            "blocked_recipes": loaded.get("blocked_recipes", []),
            "history": loaded.get("history", []),
        }
        self._ensure_week(monday_of())
        self._publish()

    async def async_save(self) -> None:
        await self.store.async_save(self.state)
        self._publish()

    def _publish(self) -> None:
        self.coordinator.async_set_updated_data(self.snapshot())

    @staticmethod
    def _week_key(monday: date) -> str:
        return monday.isoformat()

    def _ensure_week(self, monday: date) -> dict[str, Any]:
        key = self._week_key(monday)
        if key not in self.state.setdefault("weeks", {}):
            self.state["weeks"][key] = {
                "start": key,
                "days": [
                    {
                        "date": (monday + timedelta(days=index)).isoformat(),
                        "name": DAY_NAMES[index],
                        "selected": None,
                        "suggestions": [],
                        "locked": False,
                        "manual": False,
                    }
                    for index in range(7)
                ],
            }
        return self.state["weeks"][key]

    def get_week(self, offset: int = 0) -> dict[str, Any]:
        return self._ensure_week(monday_of() + timedelta(days=offset * 7))

    def all_recipes(self) -> list[dict[str, Any]]:
        result = [deepcopy(recipe) for recipe in BUILTIN_RECIPES]
        result.extend(deepcopy(self.state.get("imported_recipes", [])))
        result.extend(deepcopy(self.state.get("internet_recipes", [])))
        dedup: dict[str, dict[str, Any]] = {}
        for recipe in result:
            recipe_id = recipe.get("id")
            if recipe_id:
                dedup[recipe_id] = recipe
        return list(dedup.values())

    def _recent_ids(self) -> set[str]:
        cutoff = date.today() - timedelta(days=int(self.options["repeat_block_days"]))
        ids: set[str] = set()
        for row in self.state.get("history", []):
            try:
                if date.fromisoformat(row["date"]) >= cutoff and row.get("recipe_id"):
                    ids.add(row["recipe_id"])
            except (KeyError, TypeError, ValueError):
                continue
        return ids

    @staticmethod
    def _counts(week: dict[str, Any]) -> dict[str, int]:
        counts = {
            "fish": 0,
            "vegetarian": 0,
            "meat": 0,
            "pasta": 0,
            "rice": 0,
            "potatoes": 0,
            "special": 0,
        }
        for day in week["days"]:
            selected = day.get("selected")
            if not isinstance(selected, dict):
                continue
            for tag in selected.get("tags", []):
                if tag in counts:
                    counts[tag] += 1
            if selected.get("special"):
                counts["special"] += 1
        return counts

    def _score(self, recipe: dict[str, Any], day_index: int, counts: dict[str, int], desired_special: bool = False) -> float:
        blocked = _csv(self.options["blocked_ingredients"])
        preferred = _csv(self.options["preferred_ingredients"])
        pantry = _csv(self.options["pantry_staples"])
        ingredients = " ".join(recipe.get("ingredients", [])).casefold()
        name = recipe.get("name", "").casefold()
        description = recipe.get("description", "").casefold()
        blob = f"{name} {description} {ingredients}"

        recipe_id = recipe.get("id")
        if recipe_id in self.state.get("blocked_recipes", []):
            return -10000
        if any(term in blob for term in blocked):
            return -10000

        penalty = -120 if recipe_id in self._recent_ids() else 0
        tags = set(recipe.get("tags", []))
        limits = {
            "fish": int(self.options["fish_max"]),
            "vegetarian": int(self.options["vegetarian_max"]),
            "meat": int(self.options["meat_max"]),
            "pasta": int(self.options["pasta_max"]),
            "rice": int(self.options["rice_max"]),
            "potatoes": int(self.options["potatoes_max"]),
        }
        for tag, limit in limits.items():
            if tag in tags and counts.get(tag, 0) >= limit:
                return -9500
        if recipe.get("special") and counts.get("special", 0) >= int(self.options["special_max"]):
            return -9500

        max_minutes = int(
            self.options["weekend_max_minutes"] if day_index >= 5 else self.options["weekday_max_minutes"]
        )
        if int(recipe.get("minutes") or 45) > max_minutes:
            penalty -= 150

        pantry_hits = sum(1 for term in pantry if term and term in blob)
        preferred_hits = sum(1 for term in preferred if term and term in blob)
        rating = int(self.state.get("ratings", {}).get(recipe_id, 0))
        score = 30 + pantry_hits * 4 + preferred_hits * 10 + rating * 8 + penalty

        minimums = {
            "fish": int(self.options["fish_min"]),
            "vegetarian": int(self.options["vegetarian_min"]),
            "meat": int(self.options["meat_min"]),
        }
        for tag, minimum in minimums.items():
            if counts.get(tag, 0) < minimum:
                score += 45 if tag in tags else -5

        source_type = recipe.get("source_type")
        if desired_special:
            score += 80 if recipe.get("special") else 0
            score += 24 if source_type in {"themealdb", "imported"} else 0
        else:
            score += 22 if not recipe.get("special") else -5

        # Small deterministic randomness keeps suggestions fresh without overriding rules.
        score += random.random() * 18
        return score

    @staticmethod
    def _diversity_key(recipe: dict[str, Any]) -> tuple[str, str]:
        return (str(recipe.get("family") or ""), str(recipe.get("primary") or ""))

    def generate_day(self, day_index: int, week_offset: int = 0) -> None:
        week = self.get_week(week_offset)
        day = week["days"][day_index]
        if day.get("locked") and day.get("selected"):
            return

        counts = self._counts(week)
        recipes = self.all_recipes()
        everyday = sorted(
            recipes,
            key=lambda recipe: self._score(recipe, day_index, counts, False),
            reverse=True,
        )
        special = sorted(
            recipes,
            key=lambda recipe: self._score(recipe, day_index, counts, True),
            reverse=True,
        )

        picked: list[dict[str, Any]] = []
        seen_families: set[str] = set()
        seen_primary: set[str] = set()
        for recipe in everyday:
            if self._score(recipe, day_index, counts, False) <= -9000:
                continue
            family, primary = self._diversity_key(recipe)
            if family and family in seen_families:
                continue
            if primary and primary in seen_primary and len(picked) == 1:
                continue
            picked.append(recipe)
            if family:
                seen_families.add(family)
            if primary:
                seen_primary.add(primary)
            if len(picked) == 2:
                break

        for recipe in special:
            if self._score(recipe, day_index, counts, True) <= -9000:
                continue
            if recipe.get("id") in {item.get("id") for item in picked}:
                continue
            family, _primary = self._diversity_key(recipe)
            if family and family in seen_families:
                continue
            picked.append(recipe)
            break

        day["suggestions"] = picked[:3]

    def _internet_sync_due(self) -> bool:
        if not self.options[CONF_INTERNET_ENABLED]:
            return False
        if not str(self.options.get(CONF_THEMEALDB_API_KEY, "")).strip():
            return False
        if not self.state.get("internet_recipes"):
            return True
        raw = self.state.get("internet_last_sync")
        if not raw:
            return True
        try:
            last_sync = datetime.fromisoformat(raw)
        except (TypeError, ValueError):
            return True
        return datetime.now() - last_sync >= timedelta(days=int(self.options[CONF_INTERNET_SYNC_DAYS]))

    async def async_generate_week(self, week_offset: int = 0) -> None:
        if self._internet_sync_due():
            try:
                await self.async_refresh_internet()
            except ProviderError:
                # Meal planning remains fully functional with the built-in catalog.
                pass
        week = self.get_week(week_offset)
        for index, day in enumerate(week["days"]):
            if not day.get("locked"):
                self.generate_day(index, week_offset)
        await self.async_save()

    async def async_generate_day(self, day_index: int, week_offset: int = 0) -> None:
        self.generate_day(day_index, week_offset)
        await self.async_save()

    async def async_select(self, day_index: int, suggestion_index: int, week_offset: int = 0) -> None:
        day = self.get_week(week_offset)["days"][day_index]
        suggestions = day.get("suggestions", [])
        if suggestion_index < 0 or suggestion_index >= len(suggestions):
            raise ValueError("invalid_suggestion")
        day["selected"] = deepcopy(suggestions[suggestion_index])
        day["manual"] = False
        self._record_history(day)
        # Recalculate open days so their suggestions immediately reflect the new weekly counts.
        week = self.get_week(week_offset)
        for index, other_day in enumerate(week["days"]):
            if index != day_index and not other_day.get("selected") and not other_day.get("locked"):
                self.generate_day(index, week_offset)
        await self.async_save()

    async def async_manual(self, day_index: int, text: str, week_offset: int = 0) -> None:
        day = self.get_week(week_offset)["days"][day_index]
        day["selected"] = {
            "id": None,
            "name": text.strip(),
            "tags": [],
            "special": False,
            "source": "Freitext",
            "source_type": "manual",
            "ingredients": [],
            "instructions": [],
        }
        day["manual"] = True
        self._record_history(day)
        await self.async_save()

    async def async_clear(self, day_index: int, week_offset: int = 0) -> None:
        day = self.get_week(week_offset)["days"][day_index]
        day["selected"] = None
        day["manual"] = False
        await self.async_save()

    async def async_lock(self, day_index: int, locked: bool, week_offset: int = 0) -> None:
        self.get_week(week_offset)["days"][day_index]["locked"] = locked
        await self.async_save()

    async def async_rate(self, recipe_id: str, rating: int) -> None:
        self.state.setdefault("ratings", {})[recipe_id] = max(-2, min(2, int(rating)))
        await self.async_save()

    async def async_block(self, recipe_id: str) -> None:
        blocked = self.state.setdefault("blocked_recipes", [])
        if recipe_id not in blocked:
            blocked.append(recipe_id)
        await self.async_save()

    def _record_history(self, day: dict[str, Any]) -> None:
        selected = day.get("selected") or {}
        self.state.setdefault("history", []).append(
            {
                "date": day["date"],
                "recipe_id": selected.get("id"),
                "name": selected.get("name"),
            }
        )
        self.state["history"] = self.state["history"][-365:]

    async def async_import_url(self, url: str) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        async with session.get(
            url,
            timeout=20,
            headers={"User-Agent": "HomeAssistant SmartMealPlanner/1.1.2"},
        ) as response:
            response.raise_for_status()
            html = await response.text()
        recipe = extract_recipe(html, url)
        if not recipe:
            raise ValueError("recipe_not_found")
        imported = self.state.setdefault("imported_recipes", [])
        imported[:] = [item for item in imported if item.get("url") != url]
        imported.append(recipe)
        await self.async_save()
        return recipe

    async def async_refresh_internet(self) -> int:
        if not self.options[CONF_INTERNET_ENABLED]:
            raise ProviderError("provider_disabled")
        key = str(self.options.get(CONF_THEMEALDB_API_KEY, "")).strip()
        if not key:
            raise ProviderError("missing_api_key")
        provider = TheMealDBProvider(self.hass, key)
        rows = await provider.async_catalog()
        if not rows:
            raise ProviderError("empty_catalog")
        self.state["internet_recipes"] = rows
        self.state["internet_last_sync"] = datetime.now().isoformat(timespec="seconds")
        await self.async_save()
        return len(rows)

    def _recipe_for_display(self, recipe: dict[str, Any] | None) -> dict[str, Any] | None:
        if not isinstance(recipe, dict):
            return recipe

        recipe_id = recipe.get("id")
        if recipe_id in BUILTIN_RECIPE_MAP:
            result = deepcopy(BUILTIN_RECIPE_MAP[recipe_id])
        else:
            result = deepcopy(recipe)

        details = result.get("ingredient_details")
        if isinstance(details, list) and details:
            base_servings = int(result.get("base_servings") or result.get("servings") or 2)
            target_servings = max(1, int(self.options["household_size"]))
            factor = target_servings / max(1, base_servings)
            result["ingredients"] = [
                format_ingredient_detail(detail, factor)
                for detail in details
                if isinstance(detail, dict) and detail.get("name")
            ]
            result["servings"] = target_servings
            result["base_servings"] = base_servings
        return result

    def snapshot(self) -> dict[str, Any]:
        week = deepcopy(self.get_week(0)) if self.state else {"days": []}
        for day in week.get("days", []):
            if day.get("selected"):
                day["selected"] = self._recipe_for_display(day["selected"])
            day["suggestions"] = [
                self._recipe_for_display(recipe) for recipe in day.get("suggestions", [])
            ]
        today = date.today().isoformat()
        selected_today = next(
            (day.get("selected") for day in week.get("days", []) if day.get("date") == today),
            None,
        )
        return {
            "integration": "smart_meal_planner",
            "week": week,
            "today": selected_today,
            "recipe_count": len(self.all_recipes()) if self.state else len(BUILTIN_RECIPES),
            "builtin_count": len(BUILTIN_RECIPES),
            "imported_count": len(self.state.get("imported_recipes", [])) if self.state else 0,
            "internet_count": len(self.state.get("internet_recipes", [])) if self.state else 0,
            "internet_last_sync": self.state.get("internet_last_sync") if self.state else None,
            "internet_enabled": bool(self.options[CONF_INTERNET_ENABLED]),
            "household_size": int(self.options["household_size"]),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
