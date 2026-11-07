"""
Unit tests for taxonomy matcher, word boundaries, and false-positive filters.
"""

import unittest
from src.taxonomy import Taxonomy


class TestTaxonomy(unittest.TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy("config/taxonomy.yaml")

    def test_word_boundaries_prevent_substring_collision(self):
        # "beginning" must not match "beg" cue
        text_with_beginning = "And the servants are beginning to smell it."
        matched = self.taxonomy.match_hook_cues(text_with_beginning)
        if matched:
            self.assertNotEqual(matched["id"], "public_humiliation")

        # "beg me" must match public_humiliation
        text_with_beg = "You will beg me for mercy."
        matched_beg = self.taxonomy.match_hook_cues(text_with_beg)
        self.assertIsNotNone(matched_beg)
        self.assertEqual(matched_beg["id"], "public_humiliation")

    def test_inanimate_objects_filtered_from_physical_aggression(self):
        # Striking flint or striking a judge's gavel is NOT interpersonal violence
        flint_text = "He strikes flint and steel together over dry kindling, igniting bright sparks."
        matched_flint = self.taxonomy.match_hook_cues(flint_text)
        if matched_flint:
            self.assertNotEqual(matched_flint["id"], "physical_aggression")

        gavel_text = "The Judge furiously raises his wooden gavel and strikes the sound block."
        matched_gavel = self.taxonomy.match_hook_cues(gavel_text)
        if matched_gavel:
            self.assertNotEqual(matched_gavel["id"], "physical_aggression")

        # True physical aggression against a person MUST match
        slap_text = "Clarissa steps forward and viciously slaps Juliana across the face."
        matched_slap = self.taxonomy.match_hook_cues(slap_text)
        self.assertIsNotNone(matched_slap)
        self.assertEqual(matched_slap["id"], "physical_aggression")


if __name__ == "__main__":
    unittest.main()
