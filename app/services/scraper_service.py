"""Utilities for scraping recipe content from the web."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import trafilatura

from .nutrition_service import NutritionService


class ScraperService:
    """Extract recipe data from a remote web page."""

    INGREDIENT_PATTERN = re.compile(r"^[-•]\s*")
    NUMBER_PATTERN = re.compile(r"(\d+)")

    def __init__(self, nutrition_service: Optional[NutritionService] = None) -> None:
        self.nutrition_service = nutrition_service or NutritionService()

    @classmethod
    def scrape_recipe(cls, url: str) -> Dict[str, Any]:
        instance = cls()
        return instance._scrape(url)

    def _scrape(self, url: str) -> Dict[str, Any]:
        if not url:
            raise ValueError("A URL must be provided")

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError("Unable to retrieve the requested URL")

        extracted = trafilatura.extract(downloaded, include_comments=False, include_links=False)
        if not extracted:
            raise ValueError("Unable to extract recipe content from the page")

        return self._parse_extracted_text(extracted, url)

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_extracted_text(self, text: str, url: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("Extracted content was empty")

        title = lines[0]
        description = ""
        ingredients: List[Dict[str, Any]] = []
        instructions: List[str] = []
        prep_time = cook_time = servings = None

        section: Optional[str] = None
        for line in lines[1:]:
            lower = line.lower()
            if lower.startswith("ingredients"):
                section = "ingredients"
                continue
            if lower.startswith("instructions"):
                section = "instructions"
                continue
            if lower.startswith("prep time"):
                prep_time = self._extract_number(line)
                continue
            if lower.startswith("cook time"):
                cook_time = self._extract_number(line)
                continue
            if lower.startswith("servings"):
                servings = self._extract_number(line)
                continue

            if section == "ingredients":
                ingredients.append(self._parse_ingredient(line))
            elif section == "instructions":
                instructions.append(self._normalise_instruction(line))
            elif not description:
                description = line

        instructions_text = "\n".join(instructions) if instructions else ""
        nutrition = self.nutrition_service.calculate_nutrition(ingredients)

        return {
            "title": title,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions_text,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "servings": servings,
            "image_url": None,
            "source_url": url,
            "nutrition": nutrition,
        }

    def _parse_ingredient(self, line: str) -> Dict[str, Any]:
        line = self.INGREDIENT_PATTERN.sub("", line)
        tokens = line.split()
        if not tokens:
            return {"name": line, "amount": None, "unit": None}

        name_tokens = tokens
        amount: Optional[float] = None
        unit: Optional[str] = None

        try:
            amount = float(tokens[0])
            name_tokens = tokens[1:]
            if name_tokens:
                unit = name_tokens[0]
                name_tokens = name_tokens[1:]
        except ValueError:
            pass

        name = " ".join(name_tokens) if name_tokens else (unit or line)
        return {"name": name, "amount": amount, "unit": unit}

    @staticmethod
    def _normalise_instruction(line: str) -> str:
        return line.lstrip("0123456789.-) ")

    @staticmethod
    def _extract_number(text: str) -> Optional[int]:
        match = ScraperService.NUMBER_PATTERN.search(text)
        if match:
            return int(match.group(1))
        return None


__all__ = ["ScraperService"]
