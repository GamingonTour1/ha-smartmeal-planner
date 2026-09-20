# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Button platform for Smart Meal Planner."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .const import CONF_INTERNET_ENABLED, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GenerateWeekButton(runtime, entry), RefreshInternetButton(runtime, entry)])


class GenerateWeekButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Woche neu vorschlagen"
    _attr_icon = "mdi:calendar-refresh"

    def __init__(self, runtime, entry):
        self.runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_generate_week"

    async def async_press(self):
        await self.runtime.async_generate_week()


class RefreshInternetButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Online-Katalog synchronisieren"
    _attr_icon = "mdi:cloud-sync"

    def __init__(self, runtime, entry):
        self.runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_refresh_internet"

    @property
    def available(self) -> bool:
        return bool(self.runtime.options[CONF_INTERNET_ENABLED])

    async def async_press(self):
        await self.runtime.async_refresh_internet()
