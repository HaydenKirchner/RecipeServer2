"""Nutrition calculation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping


@dataclass
class NormalisedIngredient:
    name: str
    amount: float
    unit: str


class NutritionService:
    """Estimate nutritional information for a set of ingredients."""

    # Basic nutritional database – values per 100g.  These values are
    # intentionally conservative and designed to provide consistent output for
    # automated tests rather than precise dietary information.
    NUTRITION_DB: Mapping[str, Mapping[str, float]] = {
        "flour": {"calories": 364, "protein": 10.0, "carbs": 76.0, "fat": 1.0, "sugar": 0.3, "sodium": 2.0, "fiber": 2.7},
        "sugar": {"calories": 387, "protein": 0.0, "carbs": 100.0, "fat": 0.0, "sugar": 100.0, "sodium": 1.0, "fiber": 0.0},
        "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.0, "sugar": 0.1, "sodium": 11.0, "fiber": 0.0},
        "egg": {"calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0, "sugar": 1.1, "sodium": 124.0, "fiber": 0.0},
        "milk": {"calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0, "sugar": 5.0, "sodium": 44.0, "fiber": 0.0},
        "oil": {"calories": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "sugar": 0.0, "sodium": 0.0, "fiber": 0.0},
        "salt": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "sugar": 0.0, "sodium": 38758.0, "fiber": 0.0},
    }

    UNIT_TO_GRAMS: Mapping[str, float] = {
        "g": 1.0,
        "gram": 1.0,
        "grams": 1.0,
        "kg": 1000.0,
        "mg": 0.001,
        "oz": 28.3495,
        "ounce": 28.3495,
        "lb": 453.592,
        "pound": 453.592,
        "tsp": 4.2,
        "teaspoon": 4.2,
        "tbsp": 14.3,
        "tablespoon": 14.3,
        "cup": 120.0,
        "ml": 1.0,
        "l": 1000.0,
        "whole": 50.0,  # Rough average for eggs/fruit
        "unit": 50.0,
    }

    DEFAULT_KEYS: Iterable[str] = ("calories", "protein", "carbs", "fat", "sugar", "sodium", "fiber")

    def calculate_nutrition(self, ingredients: Iterable[Any]) -> Dict[str, float]:
        normalised = self._normalise_ingredients(ingredients)

        totals: MutableMapping[str, float] = {key: 0.0 for key in self.DEFAULT_KEYS}
        for ingredient in normalised:
            profile = self._lookup_profile(ingredient.name)
            grams = self._to_grams(ingredient.amount, ingredient.unit)
            multiplier = grams / 100.0
            for key in self.DEFAULT_KEYS:
                totals[key] += profile.get(key, 0.0) * multiplier

        return {key: round(value, 2) for key, value in totals.items()}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _normalise_ingredients(self, ingredients: Iterable[Any]) -> List[NormalisedIngredient]:
        normalised: List[NormalisedIngredient] = []
        for item in ingredients:
            if isinstance(item, str):
                normalised.append(NormalisedIngredient(name=item.lower(), amount=1.0, unit="unit"))
                continue

            name = str(item.get("name", "")).lower()
            amount = float(item.get("amount", 1.0) or 1.0)
            unit = str(item.get("unit", "g")).lower()
            normalised.append(NormalisedIngredient(name=name, amount=amount, unit=unit))

        return normalised

    def _lookup_profile(self, name: str) -> Mapping[str, float]:
        for key, profile in self.NUTRITION_DB.items():
            if key in name:
                return profile
        return {key: 0.0 for key in self.DEFAULT_KEYS}

    def _to_grams(self, amount: float, unit: str) -> float:
        conversion = self.UNIT_TO_GRAMS.get(unit.lower())
        if conversion is None:
            return amount
        return amount * conversion


__all__ = ["NutritionService"]
