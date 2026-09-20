# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Import recipes from schema.org Recipe JSON-LD."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
import re
from typing import Any


class _JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ld = False
        self.buf: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.casefold() != "script":
            return
        data = dict(attrs)
        if data.get("type", "").casefold() == "application/ld+json":
            self.in_ld = True
            self.buf = []

    def handle_data(self, data):
        if self.in_ld:
            self.buf.append(data)

    def handle_endtag(self, tag):
        if tag.casefold() == "script" and self.in_ld:
            self.blocks.append("".join(self.buf))
            self.in_ld = False
            self.buf = []


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _is_recipe_type(value: Any) -> bool:
    if isinstance(value, str):
        return value.casefold() == "recipe"
    if isinstance(value, list):
        return any(isinstance(item, str) and item.casefold() == "recipe" for item in value)
    return False


def _duration_minutes(raw: Any) -> int | None:
    if not isinstance(raw, str) or not raw.startswith("P"):
        return None
    hours = re.search(r"(\d+)H", raw)
    minutes = re.search(r"(\d+)M", raw)
    total = (int(hours.group(1)) * 60 if hours else 0) + (int(minutes.group(1)) if minutes else 0)
    return total or None


def _instructions(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, str):
        text = value.strip()
        if text:
            result.append(text)
    elif isinstance(value, list):
        for item in value:
            result.extend(_instructions(item))
    elif isinstance(value, dict):
        if isinstance(value.get("text"), str) and value["text"].strip():
            result.append(value["text"].strip())
        elif "itemListElement" in value:
            result.extend(_instructions(value["itemListElement"]))
    return result


def _publisher_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "Internet")
    if isinstance(value, str):
        return value
    return "Internet"


def extract_recipe(html: str, url: str) -> dict[str, Any] | None:
    parser = _JsonLdParser()
    parser.feed(html)
    for block in parser.blocks:
        try:
            data = json.loads(block)
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _walk(data):
            if not _is_recipe_type(node.get("@type")):
                continue

            image = node.get("image")
            if isinstance(image, list):
                image = image[0] if image else None
            if isinstance(image, dict):
                image = image.get("url")

            ingredients = node.get("recipeIngredient") or []
            if not isinstance(ingredients, list):
                ingredients = []

            total = _duration_minutes(node.get("totalTime")) or _duration_minutes(node.get("cookTime")) or 45
            cuisine = node.get("recipeCuisine")
            category = node.get("recipeCategory")
            merged = f"{cuisine or ''} {category or ''} {node.get('name', '')} {' '.join(map(str, ingredients))}".casefold()
            tags: list[str] = []
            if any(token in merged for token in ["fish", "fisch", "salmon", "lachs", "tuna", "thunfisch", "garnelen", "shrimp"]):
                tags.append("fish")
            if any(token in merged for token in ["vegetarian", "vegetarisch", "vegan"]):
                tags.append("vegetarian")
            if any(token in merged for token in ["beef", "rind", "chicken", "hähnchen", "pork", "schwein", "hackfleisch"]):
                tags.append("meat")
            if any(token in merged for token in ["pasta", "nudel", "spaghetti", "penne"]):
                tags.append("pasta")
            if any(token in merged for token in ["rice", "reis"]):
                tags.append("rice")
            if any(token in merged for token in ["potato", "kartoffel"]):
                tags.append("potatoes")

            identifier = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
            return {
                "id": f"imported_{identifier}",
                "name": node.get("name") or "Importiertes Rezept",
                "description": str(node.get("description") or ""),
                "minutes": total,
                "servings": node.get("recipeYield"),
                "special": True,
                "tags": list(dict.fromkeys(tags)),
                "ingredients": [str(item) for item in ingredients],
                "instructions": _instructions(node.get("recipeInstructions")),
                "source": _publisher_name(node.get("publisher")),
                "source_type": "imported",
                "url": url,
                "image": image,
                "category": category,
                "area": cuisine,
                "family": "imported",
                "primary": "imported",
            }
    return None
