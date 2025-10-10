"""PDF generation helpers."""
from __future__ import annotations

import os
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class PDFService:
    """Generate PDF representations of recipes."""

    def generate_recipe_pdf(self, recipe, output_path: Optional[str] = None) -> bool:
        if recipe is None:
            return False

        output_path = output_path or os.path.join(os.getcwd(), "static", "pdfs", f"recipe_{recipe.id}.pdf")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        text = doc.beginText(40, height - 60)
        text.setFont("Helvetica-Bold", 18)
        text.textLine(recipe.title or "Recipe")
        text.setFont("Helvetica", 12)

        if recipe.description:
            text.textLine("")
            text.textLine(recipe.description)

        text.textLine("")
        text.textLine(f"Prep time: {recipe.prep_time or '-'} minutes")
        text.textLine(f"Cook time: {recipe.cook_time or '-'} minutes")
        text.textLine(f"Servings: {recipe.servings or '-'}")

        text.textLine("")
        text.textLine("Ingredients:")
        for ingredient in getattr(recipe, "ingredients", []):
            amount = ingredient.amount if ingredient.amount is not None else ""
            unit = ingredient.unit or ""
            parts = [str(part) for part in (amount, unit, ingredient.name) if part]
            text.textLine(f"  - {' '.join(parts)}")

        if getattr(recipe, "instructions", None):
            text.textLine("")
            text.textLine("Instructions:")
            for line in recipe.instructions.splitlines():
                text.textLine(f"  {line.strip()}")

        if getattr(recipe, "nutrition", None):
            nutrition = recipe.nutrition.to_dict()
            text.textLine("")
            text.textLine("Nutrition:")
            for key, value in nutrition.items():
                if key in {"id", "recipe_id"}:
                    continue
                text.textLine(f"  {key.capitalize()}: {value}")

        doc.drawText(text)
        doc.showPage()
        doc.save()
        return True


__all__ = ["PDFService"]
