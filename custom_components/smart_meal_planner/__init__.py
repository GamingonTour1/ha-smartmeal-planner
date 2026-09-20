# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Smart Meal Planner integration."""
from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PANEL_MODULE_URL, PANEL_URL, PLATFORMS
from .planner import MealPlannerRuntime
from .provider import ProviderError

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _runtime(hass: HomeAssistant) -> MealPlannerRuntime:
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise ServiceValidationError("Smart Meal Planner is not configured.")
    return next(iter(entries.values()))


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up shared frontend and actions."""
    hass.data.setdefault(DOMAIN, {})

    frontend_dir = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(f"/api/{DOMAIN}/frontend", str(frontend_dir), False)]
    )

    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL,
            webcomponent_name="smart-meal-planner-panel",
            sidebar_title="Essensplan",
            sidebar_icon="mdi:food-variant",
            module_url=PANEL_MODULE_URL,
            config={"domain": DOMAIN},
            require_admin=False,
        )
    except ValueError as err:
        _LOGGER.debug("Panel already registered: %s", err)

    async def generate_week(call: ServiceCall):
        await _runtime(hass).async_generate_week(int(call.data.get("week_offset", 0)))

    async def generate_day(call: ServiceCall):
        await _runtime(hass).async_generate_day(
            int(call.data["day_index"]), int(call.data.get("week_offset", 0))
        )

    async def select_suggestion(call: ServiceCall):
        try:
            await _runtime(hass).async_select(
                int(call.data["day_index"]),
                int(call.data["suggestion_index"]),
                int(call.data.get("week_offset", 0)),
            )
        except ValueError as err:
            raise ServiceValidationError("The selected suggestion is no longer available.") from err

    async def set_manual_meal(call: ServiceCall):
        text = str(call.data["text"]).strip()
        if not text:
            raise ServiceValidationError("Meal text must not be empty.")
        await _runtime(hass).async_manual(
            int(call.data["day_index"]), text, int(call.data.get("week_offset", 0))
        )

    async def clear_day(call: ServiceCall):
        await _runtime(hass).async_clear(
            int(call.data["day_index"]), int(call.data.get("week_offset", 0))
        )

    async def set_day_lock(call: ServiceCall):
        await _runtime(hass).async_lock(
            int(call.data["day_index"]),
            bool(call.data["locked"]),
            int(call.data.get("week_offset", 0)),
        )

    async def rate_recipe(call: ServiceCall):
        await _runtime(hass).async_rate(str(call.data["recipe_id"]), int(call.data["rating"]))

    async def block_recipe(call: ServiceCall):
        await _runtime(hass).async_block(str(call.data["recipe_id"]))

    async def import_recipe_url(call: ServiceCall):
        try:
            recipe = await _runtime(hass).async_import_url(str(call.data["url"]))
            return {"name": recipe["name"], "url": recipe.get("url")}
        except Exception as err:
            raise ServiceValidationError(f"Recipe import failed: {err}") from err

    async def refresh_internet(call: ServiceCall):
        try:
            count = await _runtime(hass).async_refresh_internet()
            return {"count": count}
        except ProviderError as err:
            raise ServiceValidationError(f"Online catalog sync failed: {err}") from err

    day_schema = vol.Schema(
        {
            vol.Required("day_index"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
            vol.Optional("week_offset", default=0): vol.Coerce(int),
        }
    )

    hass.services.async_register(
        DOMAIN,
        "generate_week",
        generate_week,
        schema=vol.Schema({vol.Optional("week_offset", default=0): vol.Coerce(int)}),
    )
    hass.services.async_register(DOMAIN, "generate_day", generate_day, schema=day_schema)
    hass.services.async_register(
        DOMAIN,
        "select_suggestion",
        select_suggestion,
        schema=vol.Schema(
            {
                vol.Required("day_index"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                vol.Required("suggestion_index"): vol.All(vol.Coerce(int), vol.Range(min=0, max=2)),
                vol.Optional("week_offset", default=0): vol.Coerce(int),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "set_manual_meal",
        set_manual_meal,
        schema=vol.Schema(
            {
                vol.Required("day_index"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                vol.Required("text"): cv.string,
                vol.Optional("week_offset", default=0): vol.Coerce(int),
            }
        ),
    )
    hass.services.async_register(DOMAIN, "clear_day", clear_day, schema=day_schema)
    hass.services.async_register(
        DOMAIN,
        "set_day_lock",
        set_day_lock,
        schema=vol.Schema(
            {
                vol.Required("day_index"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                vol.Required("locked"): cv.boolean,
                vol.Optional("week_offset", default=0): vol.Coerce(int),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "rate_recipe",
        rate_recipe,
        schema=vol.Schema(
            {
                vol.Required("recipe_id"): cv.string,
                vol.Required("rating"): vol.All(vol.Coerce(int), vol.Range(min=-2, max=2)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        "block_recipe",
        block_recipe,
        schema=vol.Schema({vol.Required("recipe_id"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        "import_recipe_url",
        import_recipe_url,
        schema=vol.Schema({vol.Required("url"): cv.url}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "refresh_internet",
        refresh_internet,
        schema=vol.Schema({}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up a config entry."""
    runtime = MealPlannerRuntime(hass, entry)
    await runtime.async_load()
    hass.data[DOMAIN][entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
