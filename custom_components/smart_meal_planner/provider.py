# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Online recipe providers."""
from __future__ import annotations

import asyncio
from string import ascii_lowercase
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession


class ProviderError(Exception):
    """Raised when an online recipe provider cannot be used."""


class TheMealDBProvider:
    """Client for TheMealDB V1 API.

    The integration does not bundle an API key. Users who enable the provider must
    supply their own key.
    """

    BASE_URL = "https://www.themealdb.com/api/json/v1"

    def __init__(self, hass, api_key: str):
        self.hass = hass
        self.api_key = api_key.strip()

    async def async_validate(self) -> None:
        """Validate credentials with a small list request."""
        if not self.api_key:
            raise ProviderError("missing_api_key")
        session = async_get_clientsession(self.hass)
        url = f"{self.BASE_URL}/{self.api_key}/categories.php"
        try:
            async with session.get(url, timeout=15) as response:
                if response.status in {401, 403}:
                    raise ProviderError("invalid_api_key")
                response.raise_for_status()
                payload = await response.json()
        except ProviderError:
            raise
        except Exception as err:
            raise ProviderError("cannot_connect") from err
        if not isinstance(payload, dict) or not payload.get("categories"):
            raise ProviderError("invalid_response")

    async def async_catalog(self) -> list[dict[str, Any]]:
        """Fetch the recipe catalog accessible to the configured API key."""
        if not self.api_key:
            raise ProviderError("missing_api_key")

        session = async_get_clientsession(self.hass)
        semaphore = asyncio.Semaphore(4)

        async def fetch_letter(letter: str) -> list[dict[str, Any]]:
            url = f"{self.BASE_URL}/{self.api_key}/search.php?f={letter}"
            try:
                async with semaphore:
                    async with session.get(url, timeout=20) as response:
                        if response.status in {401, 403}:
                            raise ProviderError("invalid_api_key")
                        response.raise_for_status()
                        payload = await response.json()
            except ProviderError:
                raise
            except Exception as err:
                raise ProviderError("cannot_connect") from err
            meals = payload.get("meals") if isinstance(payload, dict) else None
            if meals is None:
                return []
            if not isinstance(meals, list):
                raise ProviderError("invalid_response")
            return [self._normalize(meal) for meal in meals if isinstance(meal, dict)]

        results = await asyncio.gather(*(fetch_letter(letter) for letter in ascii_lowercase))
        dedup: dict[str, dict[str, Any]] = {}
        for batch in results:
            for recipe in batch:
                dedup[recipe["id"]] = recipe
        return sorted(dedup.values(), key=lambda recipe: recipe["name"].casefold())

    @staticmethod
    def _split_instructions(raw: str) -> list[str]:
        raw = (raw or "").replace("\r", "\n").strip()
        if not raw:
            return []
        paragraphs = [part.strip(" -\t") for part in raw.split("\n") if part.strip(" -\t")]
        if len(paragraphs) > 1:
            return paragraphs
        # Keep long source prose intact when the provider has no explicit step breaks.
        return [raw]

    def _normalize(self, meal: dict[str, Any]) -> dict[str, Any]:
        ingredients: list[str] = []
        ingredient_names: list[str] = []
        for index in range(1, 21):
            ingredient = (meal.get(f"strIngredient{index}") or "").strip()
            measure = (meal.get(f"strMeasure{index}") or "").strip()
            if ingredient:
                ingredient_names.append(ingredient)
                ingredients.append(f"{measure} {ingredient}".strip())

        category = (meal.get("strCategory") or "").strip()
        area = (meal.get("strArea") or "").strip()
        search_blob = " ".join(
            [meal.get("strMeal") or "", category, area, *ingredient_names]
        ).casefold()
        category_l = category.casefold()

        tags: list[str] = []
        if category_l == "seafood" or any(
            token in search_blob
            for token in ["salmon", "tuna", "cod", "haddock", "fish", "prawn", "shrimp", "mackerel", "sardine"]
        ):
            tags.append("fish")
        if category_l in {"vegetarian", "vegan"}:
            tags.append("vegetarian")
        if category_l in {"beef", "chicken", "lamb", "pork", "goat"}:
            tags.append("meat")
        if any(token in search_blob for token in ["pasta", "spaghetti", "penne", "linguine", "macaroni", "tagliatelle"]):
            tags.append("pasta")
        if "rice" in search_blob:
            tags.append("rice")
        if "potato" in search_blob:
            tags.append("potatoes")

        source_url = (meal.get("strSource") or "").strip()
        youtube = (meal.get("strYoutube") or "").strip()
        instructions = self._split_instructions(
            meal.get("strInstructionsDE") or meal.get("strInstructions") or ""
        )
        description_parts = [part for part in [category, area] if part]

        return {
            "id": f"themealdb_{meal.get('idMeal')}",
            "name": meal.get("strMeal") or "Recipe",
            "description": " · ".join(description_parts),
            "minutes": 45,
            "servings": None,
            "special": False,
            "tags": list(dict.fromkeys(tags)),
            "ingredients": ingredients,
            "instructions": instructions,
            "source": "TheMealDB",
            "source_type": "themealdb",
            "url": source_url,
            "youtube": youtube,
            "image": meal.get("strMealThumb"),
            "category": category,
            "area": area,
            "family": f"themealdb:{category_l or 'other'}",
            "primary": category_l or "other",
        }
