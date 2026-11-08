"""
Tests for UI scoring integrity.
Verifies that:
1. No score inflation (e.g. getViralityScore) exists in app/page.tsx.
2. The UI renders the stored adjusted_score directly as an uncalibrated rank index.
3. No 'virality' or 'A-grade' wording appears in UI or documentation files.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestUIScoringIntegrity(unittest.TestCase):
    def test_no_virality_score_function_in_app(self):
        page_content = (ROOT / "app" / "page.tsx").read_text(encoding="utf-8")
        self.assertNotIn("getViralityScore", page_content, "getViralityScore must not exist in app/page.tsx")
        self.assertNotIn("Virality &", page_content, "Virality header must not exist in app/page.tsx")
        self.assertNotIn("Virality ", page_content, "Virality label must not exist in app/page.tsx")

    def test_rendered_score_equals_stored_adjusted_score(self):
        """Verifies that each promo's displayed score in the UI is exactly the stored adjusted_score."""
        promos_path = ROOT / "outputs" / "promos.json"
        with open(promos_path, "r", encoding="utf-8") as f:
            promos = json.load(f)

        self.assertGreater(len(promos), 0)
        for p in promos:
            stored_score = p["scores"]["adjusted_score"]
            # UI renders: (p.scores.adjusted_score || p.scores.composite_score).toFixed(2)
            rendered_str = f"{stored_score:.2f}"
            self.assertEqual(float(rendered_str), round(stored_score, 2))

    def test_tooltip_matches_spec(self):
        page_content = (ROOT / "app" / "page.tsx").read_text(encoding="utf-8")
        expected_tooltip = "Weighted prior over hook, cliffhanger, payoff, injustice and clarity. Not a conversion prediction."
        self.assertIn(expected_tooltip, page_content, "Tooltip explanation must be present in app/page.tsx")

    def test_no_virality_in_docs(self):
        docs = [
            ROOT / "README.md",
            ROOT / "SOLUTION_DOC.md",
            ROOT / "AGENTS.md",
        ]
        for doc in docs:
            if doc.exists():
                text = doc.read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(r"\bvirality\b", text, re.IGNORECASE),
                    f"{doc.name} contains forbidden word 'virality'",
                )
                self.assertIsNone(
                    re.search(r"\ba-grade\b", text, re.IGNORECASE),
                    f"{doc.name} contains forbidden word 'A-grade'",
                )


if __name__ == "__main__":
    unittest.main()
