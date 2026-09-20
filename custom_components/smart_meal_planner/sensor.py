# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Sensor platform for Smart Meal Planner."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MealPlanSensor(runtime, entry)])


class MealPlanSensor(CoordinatorEntity, SensorEntity):
    """Summary sensor used by dashboards, automations and the planner panel."""

    _attr_has_entity_name = True
    _attr_name = "Wochenplan"
    _attr_icon = "mdi:silverware-fork-knife"

    def __init__(self, runtime, entry):
        super().__init__(runtime.coordinator)
        self.runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_week"

    @property
    def native_value(self):
        days = self.coordinator.data.get("week", {}).get("days", []) if self.coordinator.data else []
        selected = sum(1 for day in days if day.get("selected"))
        return f"{selected}/7 geplant"

    @property
    def extra_state_attributes(self):
        return self.coordinator.data or {}
