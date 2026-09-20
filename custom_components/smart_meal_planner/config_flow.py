# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Config flow for Smart Meal Planner."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_INTERNET_ENABLED,
    CONF_INTERNET_SYNC_DAYS,
    CONF_THEMEALDB_API_KEY,
    DEFAULT_OPTIONS,
    DOMAIN,
)
from .provider import ProviderError, TheMealDBProvider


def _number(minimum: int, maximum: int, step: int = 1) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _csv_selector() -> selector.TextSelector:
    return selector.TextSelector(selector.TextSelectorConfig(multiline=True))


class SmartMealPlannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up Smart Meal Planner."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(title="Smart Meal Planner", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SmartMealPlannerOptionsFlow()


class SmartMealPlannerOptionsFlow(config_entries.OptionsFlowWithReload):
    """Configure meal planning rules and optional online sources."""

    async def async_step_init(self, user_input=None):
        current = {**DEFAULT_OPTIONS, **self.config_entry.options}
        errors: dict[str, str] = {}

        if user_input is not None:
            if int(user_input["fish_min"]) > int(user_input["fish_max"]):
                errors["fish_min"] = "minimum_above_maximum"
            if int(user_input["vegetarian_min"]) > int(user_input["vegetarian_max"]):
                errors["vegetarian_min"] = "minimum_above_maximum"
            if int(user_input["meat_min"]) > int(user_input["meat_max"]):
                errors["meat_min"] = "minimum_above_maximum"

            if user_input[CONF_INTERNET_ENABLED] and not str(user_input.get(CONF_THEMEALDB_API_KEY, "")).strip():
                errors[CONF_THEMEALDB_API_KEY] = "missing_api_key"

            if not errors and user_input[CONF_INTERNET_ENABLED]:
                try:
                    provider = TheMealDBProvider(self.hass, str(user_input[CONF_THEMEALDB_API_KEY]))
                    await provider.async_validate()
                except ProviderError as err:
                    errors[CONF_THEMEALDB_API_KEY] = str(err)

            if not errors:
                return self.async_create_entry(title="", data=user_input)
            current = {**current, **user_input}

        schema = vol.Schema(
            {
                vol.Required("household_size", default=current["household_size"]): _number(1, 12),
                vol.Required("fish_min", default=current["fish_min"]): _number(0, 7),
                vol.Required("fish_max", default=current["fish_max"]): _number(0, 7),
                vol.Required("vegetarian_min", default=current["vegetarian_min"]): _number(0, 7),
                vol.Required("vegetarian_max", default=current["vegetarian_max"]): _number(0, 7),
                vol.Required("meat_min", default=current["meat_min"]): _number(0, 7),
                vol.Required("meat_max", default=current["meat_max"]): _number(0, 7),
                vol.Required("pasta_max", default=current["pasta_max"]): _number(0, 7),
                vol.Required("rice_max", default=current["rice_max"]): _number(0, 7),
                vol.Required("potatoes_max", default=current["potatoes_max"]): _number(0, 7),
                vol.Required("special_max", default=current["special_max"]): _number(0, 7),
                vol.Required("weekday_max_minutes", default=current["weekday_max_minutes"]): _number(10, 240, 5),
                vol.Required("weekend_max_minutes", default=current["weekend_max_minutes"]): _number(10, 360, 5),
                vol.Required("repeat_block_days", default=current["repeat_block_days"]): _number(0, 90),
                vol.Optional("blocked_ingredients", default=current["blocked_ingredients"]): _csv_selector(),
                vol.Optional("preferred_ingredients", default=current["preferred_ingredients"]): _csv_selector(),
                vol.Optional("pantry_staples", default=current["pantry_staples"]): _csv_selector(),
                vol.Required(CONF_INTERNET_ENABLED, default=current[CONF_INTERNET_ENABLED]): bool,
                vol.Optional(CONF_THEMEALDB_API_KEY, default=current[CONF_THEMEALDB_API_KEY]): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(CONF_INTERNET_SYNC_DAYS, default=current[CONF_INTERNET_SYNC_DAYS]): _number(1, 30),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
