# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Constants for Smart Meal Planner."""

DOMAIN = "smart_meal_planner"
PLATFORMS = ["sensor", "button"]
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.data"
PANEL_URL = "essensplan"
PANEL_MODULE_URL = f"/api/{DOMAIN}/frontend/panel.js"

CONF_INTERNET_ENABLED = "internet_enabled"
CONF_THEMEALDB_API_KEY = "themealdb_api_key"
CONF_INTERNET_SYNC_DAYS = "internet_sync_days"

DEFAULT_OPTIONS = {
    "household_size": 2,
    "fish_min": 0,
    "fish_max": 1,
    "vegetarian_min": 1,
    "vegetarian_max": 4,
    "meat_min": 0,
    "meat_max": 5,
    "pasta_max": 2,
    "rice_max": 2,
    "potatoes_max": 3,
    "special_max": 2,
    "weekday_max_minutes": 45,
    "weekend_max_minutes": 90,
    "repeat_block_days": 14,
    "blocked_ingredients": "",
    "preferred_ingredients": "",
    "pantry_staples": "Nudeln, Reis, Kartoffeln, Eier, Mehl, Milch, Butter, Käse, Zwiebeln, Knoblauch, Öl, Tomatenmark, Dosentomaten, Brühe, Salz, Pfeffer",
    CONF_INTERNET_ENABLED: False,
    CONF_THEMEALDB_API_KEY: "",
    CONF_INTERNET_SYNC_DAYS: 7,
}
