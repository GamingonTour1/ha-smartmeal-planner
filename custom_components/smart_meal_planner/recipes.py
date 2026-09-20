# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

"""Built-in recipe catalog for Smart Meal Planner.

The catalog is generated from curated meal families, proteins and flavour profiles.
It is intentionally stored as structured recipe data so the integration remains useful
without any external service or API key.
"""
from __future__ import annotations

from typing import Any


PROTEINS: list[dict[str, Any]] = [
    {"key": "chicken", "name": "Hähnchen", "ingredient": "Hähnchenbrust", "tag": "meat"},
    {"key": "turkey", "name": "Pute", "ingredient": "Putenbrust", "tag": "meat"},
    {"key": "beef", "name": "Rind", "ingredient": "Rindergeschnetzeltes", "tag": "meat"},
    {"key": "mince", "name": "Hackfleisch", "ingredient": "Rinderhackfleisch", "tag": "meat"},
    {"key": "pork", "name": "Schweinefilet", "ingredient": "Schweinefilet", "tag": "meat"},
    {"key": "salmon", "name": "Lachs", "ingredient": "Lachsfilet", "tag": "fish"},
    {"key": "cod", "name": "Kabeljau", "ingredient": "Kabeljaufilet", "tag": "fish"},
    {"key": "shrimp", "name": "Garnelen", "ingredient": "Garnelen", "tag": "fish"},
    {"key": "tofu", "name": "Tofu", "ingredient": "Naturtofu", "tag": "vegetarian"},
    {"key": "chickpea", "name": "Kichererbsen", "ingredient": "Kichererbsen", "tag": "vegetarian"},
    {"key": "lentil", "name": "Linsen", "ingredient": "Linsen", "tag": "vegetarian"},
    {"key": "feta", "name": "Feta", "ingredient": "Feta", "tag": "vegetarian"},
    {"key": "halloumi", "name": "Halloumi", "ingredient": "Halloumi", "tag": "vegetarian"},
    {"key": "egg", "name": "Ei", "ingredient": "Eier", "tag": "vegetarian"},
]


FLAVOURS: list[dict[str, Any]] = [
    {
        "key": "tomato_herb",
        "name": "Tomate & Kräuter",
        "ingredients": ["Dosentomaten", "Zwiebeln", "Knoblauch", "italienische Kräuter"],
        "finish": "Mit Tomaten und Kräutern abschmecken und kurz einkochen lassen.",
        "special": False,
    },
    {
        "key": "paprika_cream",
        "name": "Paprika-Creme",
        "ingredients": ["Paprika", "Zwiebeln", "Sahne oder Kochcreme", "Paprikapulver"],
        "finish": "Paprika anschwitzen, mit Kochcreme ablöschen und cremig einkochen.",
        "special": False,
    },
    {
        "key": "lemon_garlic",
        "name": "Zitrone & Knoblauch",
        "ingredients": ["Zitrone", "Knoblauch", "Olivenöl", "Petersilie"],
        "finish": "Mit Zitronensaft, Knoblauch und Petersilie frisch abschmecken.",
        "special": False,
    },
    {
        "key": "honey_mustard",
        "name": "Honig-Senf",
        "ingredients": ["Senf", "Honig", "Zwiebeln", "Brühe"],
        "finish": "Senf, Honig und etwas Brühe verrühren und kurz glasieren lassen.",
        "special": False,
    },
    {
        "key": "teriyaki",
        "name": "Teriyaki & Sesam",
        "ingredients": ["Sojasoße", "Honig", "Sesam", "Frühlingszwiebeln"],
        "finish": "Mit Sojasoße und Honig glasieren, anschließend Sesam darübergeben.",
        "special": True,
    },
    {
        "key": "curry_coconut",
        "name": "Curry & Kokos",
        "ingredients": ["Kokosmilch", "Currypulver", "Zwiebeln", "Limette"],
        "finish": "Kokosmilch und Curry zugeben und bis zur gewünschten Konsistenz köcheln.",
        "special": True,
    },
    {
        "key": "pesto",
        "name": "Pesto",
        "ingredients": ["Pesto", "Cherrytomaten", "Parmesan", "Olivenöl"],
        "finish": "Pesto erst zum Schluss unterheben und mit Parmesan servieren.",
        "special": False,
    },
    {
        "key": "mediterranean",
        "name": "Mediterran",
        "ingredients": ["Zucchini", "Paprika", "Cherrytomaten", "Olivenöl", "Kräuter"],
        "finish": "Das Gemüse bissfest garen und kräftig mit mediterranen Kräutern würzen.",
        "special": False,
    },
    {
        "key": "mushroom_cream",
        "name": "Pilz-Rahm",
        "ingredients": ["Champignons", "Zwiebeln", "Sahne oder Kochcreme", "Brühe"],
        "finish": "Pilze kräftig anbraten, mit Brühe und Kochcreme ablöschen und einkochen.",
        "special": False,
    },
    {
        "key": "chili_lime",
        "name": "Chili & Limette",
        "ingredients": ["Limette", "Chili", "Paprika", "Frühlingszwiebeln"],
        "finish": "Mit Limettensaft und Chili abschmecken und mit Frühlingszwiebeln servieren.",
        "special": True,
    },
]


FAMILIES: list[dict[str, Any]] = [
    {
        "key": "pasta",
        "label": "Pasta",
        "title": "{protein}-Pasta – {flavour}",
        "base": ["Nudeln"],
        "tags": ["pasta"],
        "minutes": 30,
        "steps": [
            "Nudeln in Salzwasser al dente kochen und etwas Kochwasser auffangen.",
            "{protein_ingredient} vorbereiten, würzen und in einer großen Pfanne garen.",
            "Die Zutaten für {flavour} in die Pfanne geben. {finish}",
            "Nudeln unterheben, bei Bedarf mit etwas Kochwasser binden und direkt servieren.",
        ],
    },
    {
        "key": "rice_pan",
        "label": "Reispfanne",
        "title": "{protein}-Reispfanne – {flavour}",
        "base": ["Reis", "Gemüse nach Wahl"],
        "tags": ["rice"],
        "minutes": 35,
        "steps": [
            "Reis nach Packungsangabe garen.",
            "{protein_ingredient} und Gemüse in einer großen Pfanne anbraten.",
            "Die Komponenten für {flavour} zufügen. {finish}",
            "Reis unterheben, kurz durchschwenken und abschmecken.",
        ],
    },
    {
        "key": "potato_pan",
        "label": "Kartoffelpfanne",
        "title": "Kartoffelpfanne mit {protein} – {flavour}",
        "base": ["Kartoffeln", "Zwiebeln"],
        "tags": ["potatoes"],
        "minutes": 40,
        "steps": [
            "Kartoffeln in kleine Stücke schneiden und in wenig Öl goldbraun garen.",
            "Zwiebeln und {protein_ingredient} zugeben und fertig garen.",
            "Die Zutaten für {flavour} einarbeiten. {finish}",
            "Alles nochmals abschmecken und heiß servieren.",
        ],
    },
    {
        "key": "traybake",
        "label": "Ofengericht",
        "title": "Ofen-{protein} mit Gemüse – {flavour}",
        "base": ["Kartoffeln oder Ofengemüse", "Gemüse nach Wahl"],
        "tags": ["potatoes"],
        "minutes": 50,
        "steps": [
            "Backofen auf 200 °C Ober-/Unterhitze vorheizen.",
            "Gemüse und Kartoffeln schneiden, würzen und auf einem Blech verteilen.",
            "{protein_ingredient} sowie die Zutaten für {flavour} ergänzen.",
            "Alles garen, bis Gemüse und Hauptzutat durchgegart sind. {finish}",
        ],
    },
    {
        "key": "wraps",
        "label": "Wraps",
        "title": "Wraps mit {protein} – {flavour}",
        "base": ["Wrap-Tortillas", "Salat", "Tomaten"],
        "tags": [],
        "minutes": 25,
        "steps": [
            "{protein_ingredient} würzen und in der Pfanne garen.",
            "Salat und Gemüse klein schneiden und die Zutaten für {flavour} vorbereiten.",
            "Tortillas kurz erwärmen und mit allen Zutaten belegen.",
            "Wraps eng einrollen und direkt servieren.",
        ],
    },
    {
        "key": "bowl",
        "label": "Bowl",
        "title": "{protein}-Bowl – {flavour}",
        "base": ["Reis", "Gurke", "Möhre", "Salat"],
        "tags": ["rice"],
        "minutes": 35,
        "steps": [
            "Reis garen und das frische Gemüse vorbereiten.",
            "{protein_ingredient} würzen und passend garen.",
            "Die Zutaten für {flavour} zu einem Dressing oder Topping verarbeiten.",
            "Alles in Schalen anrichten. {finish}",
        ],
    },
    {
        "key": "noodle_wok",
        "label": "Nudel-Wok",
        "title": "Nudel-Wok mit {protein} – {flavour}",
        "base": ["Mie-Nudeln", "Wokgemüse"],
        "tags": ["pasta"],
        "minutes": 25,
        "steps": [
            "Nudeln nach Packungsangabe vorbereiten.",
            "{protein_ingredient} in einem heißen Wok oder einer großen Pfanne anbraten.",
            "Gemüse und die Zutaten für {flavour} hinzufügen. {finish}",
            "Nudeln untermischen und alles kurz bei hoher Hitze schwenken.",
        ],
    },
    {
        "key": "gnocchi",
        "label": "Gnocchi",
        "title": "Gnocchi mit {protein} – {flavour}",
        "base": ["Gnocchi"],
        "tags": [],
        "minutes": 30,
        "steps": [
            "Gnocchi in einer großen Pfanne goldbraun anbraten und herausnehmen.",
            "{protein_ingredient} in derselben Pfanne garen.",
            "Die Zutaten für {flavour} zugeben. {finish}",
            "Gnocchi wieder unterheben und kurz ziehen lassen.",
        ],
    },
    {
        "key": "casserole",
        "label": "Auflauf",
        "title": "{protein}-Auflauf – {flavour}",
        "base": ["Nudeln oder Kartoffeln", "Käse zum Überbacken"],
        "tags": [],
        "minutes": 55,
        "steps": [
            "Backofen auf 190 °C Ober-/Unterhitze vorheizen und die Basis vorgaren.",
            "{protein_ingredient} sowie die Zutaten für {flavour} vorbereiten.",
            "Alles in einer Auflaufform vermengen und mit Käse bestreuen.",
            "Backen, bis der Auflauf goldbraun ist und vollständig durchgegart ist.",
        ],
    },
    {
        "key": "soup",
        "label": "Suppe & Eintopf",
        "title": "Eintopf mit {protein} – {flavour}",
        "base": ["Brühe", "Möhren", "Zwiebeln", "Kartoffeln"],
        "tags": ["potatoes"],
        "minutes": 45,
        "steps": [
            "Gemüse klein schneiden und in einem großen Topf anschwitzen.",
            "{protein_ingredient} zugeben und kurz mitgaren.",
            "Mit Brühe auffüllen und die Zutaten für {flavour} ergänzen.",
            "Bei mittlerer Hitze garen, bis alles weich ist. {finish}",
        ],
    },
    {
        "key": "tacos",
        "label": "Tacos",
        "title": "Tacos mit {protein} – {flavour}",
        "base": ["Taco-Schalen oder kleine Tortillas", "Salat", "Tomaten"],
        "tags": [],
        "minutes": 30,
        "steps": [
            "{protein_ingredient} würzen und kräftig anbraten.",
            "Gemüse und die Komponenten für {flavour} vorbereiten.",
            "Tortillas oder Taco-Schalen erwärmen.",
            "Alles am Tisch füllen und mit dem vorbereiteten Topping servieren.",
        ],
    },
    {
        "key": "couscous",
        "label": "Couscous",
        "title": "Couscous mit {protein} – {flavour}",
        "base": ["Couscous", "Gemüse nach Wahl", "Brühe"],
        "tags": [],
        "minutes": 25,
        "steps": [
            "Couscous mit heißer Brühe übergießen und quellen lassen.",
            "{protein_ingredient} und Gemüse separat anbraten.",
            "Die Zutaten für {flavour} zufügen. {finish}",
            "Couscous auflockern, alles vermengen und abschmecken.",
        ],
    },
    {
        "key": "risotto",
        "label": "Risotto",
        "title": "Risotto mit {protein} – {flavour}",
        "base": ["Risottoreis", "Brühe", "Parmesan"],
        "tags": ["rice"],
        "minutes": 40,
        "steps": [
            "Risottoreis mit Zwiebeln glasig anschwitzen.",
            "Brühe portionsweise zugeben und unter Rühren einkochen lassen.",
            "{protein_ingredient} separat garen und zusammen mit {flavour} einarbeiten.",
            "Zum Schluss Parmesan unterheben und cremig servieren.",
        ],
    },
    {
        "key": "flatbread",
        "label": "Fladenbrot",
        "title": "Fladenbrot mit {protein} – {flavour}",
        "base": ["Fladenbrot", "Joghurt oder Creme", "Salat"],
        "tags": [],
        "minutes": 30,
        "steps": [
            "{protein_ingredient} würzen und garen.",
            "Gemüse und die Zutaten für {flavour} vorbereiten.",
            "Fladenbrot erwärmen und aufschneiden.",
            "Mit Creme, Gemüse und Hauptzutat füllen und sofort servieren.",
        ],
    },
    {
        "key": "frittata",
        "label": "Frittata",
        "title": "Frittata mit {protein} – {flavour}",
        "base": ["Eier", "Milch", "Käse"],
        "tags": [],
        "minutes": 35,
        "steps": [
            "Backofen auf 190 °C vorheizen und Eier mit etwas Milch verquirlen.",
            "{protein_ingredient} und weitere Zutaten in einer ofenfesten Pfanne vorgaren.",
            "Die Zutaten für {flavour} ergänzen und die Eiermasse darübergeben.",
            "Im Ofen stocken lassen und anschließend in Stücke schneiden.",
        ],
    },
    {
        "key": "salad",
        "label": "Salat",
        "title": "Großer Salat mit {protein} – {flavour}",
        "base": ["Blattsalat", "Gurke", "Tomaten"],
        "tags": [],
        "minutes": 20,
        "steps": [
            "Salat und Gemüse waschen, schneiden und in eine große Schüssel geben.",
            "{protein_ingredient} passend garen oder vorbereiten.",
            "Aus den Zutaten für {flavour} ein Dressing zubereiten.",
            "Alles kurz vor dem Servieren vermengen und abschmecken.",
        ],
    },
    {
        "key": "sandwich",
        "label": "Sandwich",
        "title": "Ofen-Sandwich mit {protein} – {flavour}",
        "base": ["Ciabatta oder Sandwichbrot", "Salat", "Käse"],
        "tags": [],
        "minutes": 20,
        "steps": [
            "{protein_ingredient} und die Zutaten für {flavour} vorbereiten.",
            "Brot aufschneiden und nach Wunsch kurz anrösten.",
            "Mit Käse, Salat, Gemüse und Hauptzutat belegen.",
            "Warm oder kalt servieren und nach Geschmack ergänzen.",
        ],
    },
    {
        "key": "orzo",
        "label": "Kritharaki",
        "title": "Kritharaki mit {protein} – {flavour}",
        "base": ["Kritharaki oder Orzo", "Brühe"],
        "tags": ["pasta"],
        "minutes": 35,
        "steps": [
            "Kritharaki nach Packungsangabe garen oder direkt in Brühe köcheln.",
            "{protein_ingredient} in einer Pfanne anbraten.",
            "Die Zutaten für {flavour} hinzufügen. {finish}",
            "Kritharaki unterheben und alles cremig oder saftig fertig garen.",
        ],
    },
    {
        "key": "onepot",
        "label": "One Pot",
        "title": "One-Pot-Gericht mit {protein} – {flavour}",
        "base": ["Nudeln", "Brühe", "Gemüse nach Wahl"],
        "tags": ["pasta"],
        "minutes": 30,
        "steps": [
            "{protein_ingredient} in einem großen Topf kurz anbraten.",
            "Nudeln, Gemüse, Brühe und die Zutaten für {flavour} zugeben.",
            "Unter gelegentlichem Rühren garen, bis die Nudeln bissfest sind.",
            "{finish} Vor dem Servieren nochmals abschmecken.",
        ],
    },
    {
        "key": "burger",
        "label": "Burger",
        "title": "Burger mit {protein} – {flavour}",
        "base": ["Burgerbrötchen", "Salat", "Tomaten", "Käse"],
        "tags": [],
        "minutes": 35,
        "steps": [
            "{protein_ingredient} passend zu Burger-Patties oder als Füllung vorbereiten und garen.",
            "Die Zutaten für {flavour} zu Sauce oder Topping verarbeiten.",
            "Burgerbrötchen kurz anrösten und mit Salat und Tomaten belegen.",
            "Burger zusammensetzen und direkt servieren.",
        ],
    },
    {
        "key": "stuffed",
        "label": "Gefülltes Gemüse",
        "title": "Gefülltes Gemüse mit {protein} – {flavour}",
        "base": ["Paprika oder Zucchini", "Reis", "Käse zum Überbacken"],
        "tags": ["rice"],
        "minutes": 55,
        "steps": [
            "Backofen auf 190 °C vorheizen und Gemüse zum Füllen vorbereiten.",
            "Reis vorgaren und mit {protein_ingredient} sowie {flavour} vermengen.",
            "Gemüse füllen, in eine Form setzen und nach Wunsch mit Käse bestreuen.",
            "Backen, bis das Gemüse weich und die Füllung vollständig gegart ist.",
        ],
    },
]


# Base quantities are defined for two portions. They are kept structured so the
# frontend data can be scaled to the configured household size without parsing
# human-readable ingredient strings.
INGREDIENT_SPECS: dict[str, tuple[float, str]] = {
    "Blattsalat": (150, "g"),
    "Brühe": (250, "ml"),
    "Burgerbrötchen": (2, "Stück"),
    "Champignons": (250, "g"),
    "Cherrytomaten": (200, "g"),
    "Chili": (1, "Stück"),
    "Ciabatta oder Sandwichbrot": (2, "Stück"),
    "Couscous": (160, "g"),
    "Currypulver": (2, "TL"),
    "Dosentomaten": (400, "g"),
    "Eier": (4, "Stück"),
    "Feta": (200, "g"),
    "Fladenbrot": (2, "Stück"),
    "Frühlingszwiebeln": (2, "Stück"),
    "Garnelen": (250, "g"),
    "Gemüse nach Wahl": (300, "g"),
    "Gnocchi": (500, "g"),
    "Gurke": (150, "g"),
    "Halloumi": (200, "g"),
    "Honig": (1, "EL"),
    "Hähnchenbrust": (300, "g"),
    "Joghurt oder Creme": (150, "g"),
    "Kabeljaufilet": (300, "g"),
    "Kartoffeln": (500, "g"),
    "Kartoffeln oder Ofengemüse": (600, "g"),
    "Kichererbsen": (240, "g"),
    "Knoblauch": (2, "Zehen"),
    "Kokosmilch": (400, "ml"),
    "Kritharaki oder Orzo": (200, "g"),
    "Kräuter": (1, "TL"),
    "Käse": (100, "g"),
    "Käse zum Überbacken": (100, "g"),
    "Lachsfilet": (300, "g"),
    "Limette": (1, "Stück"),
    "Linsen": (160, "g"),
    "Mie-Nudeln": (200, "g"),
    "Milch": (80, "ml"),
    "Möhre": (150, "g"),
    "Möhren": (200, "g"),
    "Naturtofu": (300, "g"),
    "Nudeln": (200, "g"),
    "Nudeln oder Kartoffeln": (400, "g"),
    "Olivenöl": (2, "EL"),
    "Paprika": (200, "g"),
    "Paprika oder Zucchini": (2, "Stück"),
    "Paprikapulver": (1, "TL"),
    "Parmesan": (40, "g"),
    "Pesto": (100, "g"),
    "Petersilie": (15, "g"),
    "Pfeffer": (0.5, "TL"),
    "Putenbrust": (300, "g"),
    "Reis": (160, "g"),
    "Rindergeschnetzeltes": (300, "g"),
    "Rinderhackfleisch": (300, "g"),
    "Risottoreis": (160, "g"),
    "Sahne oder Kochcreme": (200, "ml"),
    "Salat": (100, "g"),
    "Salz": (1, "TL"),
    "Schweinefilet": (300, "g"),
    "Senf": (2, "EL"),
    "Sesam": (1, "EL"),
    "Sojasoße": (3, "EL"),
    "Taco-Schalen oder kleine Tortillas": (6, "Stück"),
    "Tomaten": (200, "g"),
    "Wokgemüse": (300, "g"),
    "Wrap-Tortillas": (4, "Stück"),
    "Zitrone": (1, "Stück"),
    "Zucchini": (250, "g"),
    "Zwiebeln": (1, "Stück"),
    "italienische Kräuter": (1, "TL"),
}

# Some ingredients need a family-specific quantity. For example, broth is only
# a small sauce component in one recipe family but the main liquid in a soup.
FAMILY_INGREDIENT_OVERRIDES: dict[str, dict[str, tuple[float, str]]] = {
    "pasta": {"Nudeln": (200, "g")},
    "rice_pan": {"Reis": (160, "g"), "Gemüse nach Wahl": (250, "g")},
    "potato_pan": {"Kartoffeln": (500, "g")},
    "traybake": {"Kartoffeln oder Ofengemüse": (600, "g"), "Gemüse nach Wahl": (300, "g")},
    "wraps": {"Wrap-Tortillas": (4, "Stück"), "Salat": (100, "g"), "Tomaten": (200, "g")},
    "bowl": {"Reis": (160, "g"), "Gurke": (150, "g"), "Möhre": (150, "g"), "Salat": (100, "g")},
    "noodle_wok": {"Mie-Nudeln": (200, "g"), "Wokgemüse": (300, "g")},
    "gnocchi": {"Gnocchi": (500, "g")},
    "casserole": {"Nudeln oder Kartoffeln": (400, "g"), "Käse zum Überbacken": (100, "g")},
    "soup": {"Brühe": (750, "ml"), "Möhren": (200, "g"), "Zwiebeln": (1, "Stück"), "Kartoffeln": (400, "g")},
    "tacos": {"Taco-Schalen oder kleine Tortillas": (6, "Stück"), "Salat": (100, "g"), "Tomaten": (200, "g")},
    "couscous": {"Couscous": (160, "g"), "Gemüse nach Wahl": (250, "g"), "Brühe": (250, "ml")},
    "risotto": {"Risottoreis": (160, "g"), "Brühe": (600, "ml"), "Parmesan": (50, "g")},
    "flatbread": {"Fladenbrot": (2, "Stück"), "Joghurt oder Creme": (150, "g"), "Salat": (100, "g")},
    "frittata": {"Eier": (4, "Stück"), "Milch": (80, "ml"), "Käse": (100, "g")},
    "salad": {"Blattsalat": (150, "g"), "Gurke": (150, "g"), "Tomaten": (200, "g")},
    "sandwich": {"Ciabatta oder Sandwichbrot": (2, "Stück"), "Salat": (80, "g"), "Käse": (80, "g")},
    "orzo": {"Kritharaki oder Orzo": (200, "g"), "Brühe": (500, "ml")},
    "onepot": {"Nudeln": (200, "g"), "Brühe": (600, "ml"), "Gemüse nach Wahl": (250, "g")},
    "burger": {"Burgerbrötchen": (2, "Stück"), "Salat": (80, "g"), "Tomaten": (150, "g"), "Käse": (80, "g")},
    "stuffed": {"Paprika oder Zucchini": (2, "Stück"), "Reis": (120, "g"), "Käse zum Überbacken": (80, "g")},
}

FLAVOUR_INGREDIENT_OVERRIDES: dict[str, dict[str, tuple[float, str]]] = {
    "tomato_herb": {"Dosentomaten": (400, "g"), "Zwiebeln": (1, "Stück"), "Knoblauch": (2, "Zehen"), "italienische Kräuter": (1, "TL")},
    "paprika_cream": {"Paprika": (200, "g"), "Zwiebeln": (1, "Stück"), "Sahne oder Kochcreme": (200, "ml"), "Paprikapulver": (1, "TL")},
    "lemon_garlic": {"Zitrone": (1, "Stück"), "Knoblauch": (2, "Zehen"), "Olivenöl": (2, "EL"), "Petersilie": (15, "g")},
    "honey_mustard": {"Senf": (2, "EL"), "Honig": (1, "EL"), "Zwiebeln": (1, "Stück"), "Brühe": (100, "ml")},
    "teriyaki": {"Sojasoße": (3, "EL"), "Honig": (1, "EL"), "Sesam": (1, "EL"), "Frühlingszwiebeln": (2, "Stück")},
    "curry_coconut": {"Kokosmilch": (400, "ml"), "Currypulver": (2, "TL"), "Zwiebeln": (1, "Stück"), "Limette": (1, "Stück")},
    "pesto": {"Pesto": (100, "g"), "Cherrytomaten": (200, "g"), "Parmesan": (40, "g"), "Olivenöl": (1, "EL")},
    "mediterranean": {"Zucchini": (250, "g"), "Paprika": (200, "g"), "Cherrytomaten": (200, "g"), "Olivenöl": (2, "EL"), "Kräuter": (1, "TL")},
    "mushroom_cream": {"Champignons": (250, "g"), "Zwiebeln": (1, "Stück"), "Sahne oder Kochcreme": (200, "ml"), "Brühe": (100, "ml")},
    "chili_lime": {"Limette": (1, "Stück"), "Chili": (1, "Stück"), "Paprika": (200, "g"), "Frühlingszwiebeln": (2, "Stück")},
}

PROTEIN_INGREDIENT_OVERRIDES: dict[str, tuple[float, str]] = {
    "chicken": (300, "g"),
    "turkey": (300, "g"),
    "beef": (300, "g"),
    "mince": (300, "g"),
    "pork": (300, "g"),
    "salmon": (300, "g"),
    "cod": (300, "g"),
    "shrimp": (250, "g"),
    "tofu": (300, "g"),
    "chickpea": (240, "g"),
    "lentil": (160, "g"),
    "feta": (200, "g"),
    "halloumi": (200, "g"),
    "egg": (4, "Stück"),
}


def _ingredient_detail(name: str, family: dict[str, Any], protein: dict[str, Any], flavour: dict[str, Any]) -> dict[str, Any]:
    family_spec = FAMILY_INGREDIENT_OVERRIDES.get(family["key"], {}).get(name)
    flavour_spec = FLAVOUR_INGREDIENT_OVERRIDES.get(flavour["key"], {}).get(name)
    protein_spec = PROTEIN_INGREDIENT_OVERRIDES.get(protein["key"]) if name == protein["ingredient"] else None

    # The meal family defines main-component quantities. Flavour quantities are
    # preferred for sauce components, while the protein mapping covers the main
    # protein source. This prevents, for example, soup broth from being reduced
    # to the small amount used by a sauce profile.
    if family_spec is not None:
        amount, unit = family_spec
    elif protein_spec is not None:
        amount, unit = protein_spec
    elif flavour_spec is not None:
        amount, unit = flavour_spec
    else:
        amount, unit = INGREDIENT_SPECS[name]

    if family["key"] == "frittata" and protein["key"] == "egg" and name == "Eier":
        amount, unit = 6, "Stück"

    return {"name": name, "amount": amount, "unit": unit}


COUNTABLE_INGREDIENTS: dict[str, tuple[str, str]] = {
    "Burgerbrötchen": ("Burgerbrötchen", "Burgerbrötchen"),
    "Chili": ("Chilischote", "Chilischoten"),
    "Ciabatta oder Sandwichbrot": ("Ciabatta/Sandwichbrot", "Ciabatta/Sandwichbrote"),
    "Eier": ("Ei", "Eier"),
    "Fladenbrot": ("Fladenbrot", "Fladenbrote"),
    "Frühlingszwiebeln": ("Frühlingszwiebel", "Frühlingszwiebeln"),
    "Limette": ("Limette", "Limetten"),
    "Taco-Schalen oder kleine Tortillas": ("Taco-Schale/Tortilla", "Taco-Schalen/Tortillas"),
    "Wrap-Tortillas": ("Wrap-Tortilla", "Wrap-Tortillas"),
    "Zitrone": ("Zitrone", "Zitronen"),
    "Zwiebeln": ("Zwiebel", "Zwiebeln"),
}


def _format_amount(amount: float) -> str:
    if float(amount).is_integer():
        return str(int(amount))
    return (f"{amount:.2f}".rstrip("0").rstrip(".")).replace(".", ",")


def format_ingredient_detail(detail: dict[str, Any], factor: float = 1.0) -> str:
    amount = float(detail["amount"]) * factor
    unit = str(detail["unit"])
    name = str(detail["name"])
    amount_text = _format_amount(amount)

    if unit == "Stück" and name in COUNTABLE_INGREDIENTS:
        singular, plural = COUNTABLE_INGREDIENTS[name]
        label = singular if abs(amount - 1) < 0.001 else plural
        return f"{amount_text} {label}"
    return f"{amount_text} {unit} {name}"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _build_builtin_recipes() -> list[dict[str, Any]]:
    recipes: list[dict[str, Any]] = []
    for family_index, family in enumerate(FAMILIES):
        for protein_index, protein in enumerate(PROTEINS):
            # Two deterministic flavour variations per protein and meal family.
            flavour_indexes = [
                (family_index + protein_index * 2) % len(FLAVOURS),
                (family_index * 3 + protein_index * 2 + 3) % len(FLAVOURS),
            ]
            for variant_index, flavour_index in enumerate(flavour_indexes):
                flavour = FLAVOURS[flavour_index]
                tags = list(family["tags"])
                tags.append(protein["tag"])
                if protein["tag"] == "vegetarian" and "vegetarian" not in tags:
                    tags.append("vegetarian")
                ingredient_names = _dedupe(
                    [protein["ingredient"], *family["base"], *flavour["ingredients"], "Salz", "Pfeffer"]
                )
                ingredient_details = [
                    _ingredient_detail(name, family, protein, flavour) for name in ingredient_names
                ]
                ingredients = [format_ingredient_detail(detail) for detail in ingredient_details]
                fmt = {
                    "protein": protein["name"],
                    "protein_ingredient": protein["ingredient"],
                    "flavour": flavour["name"],
                    "finish": flavour["finish"],
                }
                recipes.append(
                    {
                        "id": f"builtin_{family['key']}_{protein['key']}_{flavour['key']}_{variant_index}",
                        "name": family["title"].format(**fmt),
                        "description": f"{family['label']} mit {protein['name']} und {flavour['name']}.",
                        "minutes": int(family["minutes"]),
                        "servings": 2,
                        "base_servings": 2,
                        "special": bool(flavour["special"] or family["key"] in {"tacos", "flatbread", "burger"}),
                        "tags": tags,
                        "ingredients": ingredients,
                        "ingredient_details": ingredient_details,
                        "instructions": [step.format(**fmt) for step in family["steps"]],
                        "source": "Smart Meal Planner",
                        "source_type": "builtin",
                        "family": family["key"],
                        "primary": protein["key"],
                    }
                )
    return recipes


BUILTIN_RECIPES = _build_builtin_recipes()
