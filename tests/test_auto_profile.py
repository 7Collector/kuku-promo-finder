"""
Tests for Stage D: Auto-Profile.
- Compares config/shows/broken_soldier.generated.yaml against the hand-written profile.
- Reports matched facts, wrong facts, and missing facts.
- Tests auto-profile generation on a differently themed 3-episode screenplay written from scratch.
"""

import os
import tempfile
import unittest
import yaml
from pathlib import Path

from src.parser import parse_screenplay_text
from src.providers.base import BaseLLMProvider
from src.stages import run_auto_profile


DIFF_THEMED_EP1 = """EPISODE NUMBER: 1
EPISODE LOGLINE: In Neo-Veridia, Detective Silas Ray investigates a severed cybernetic spine.

SCENE 1
Scene heading: INT. ALLEYWAY - NIGHT
Scene start: 00:00.00
Scene end: 00:45.00

**SILAS (Gravelly):**
Start: (00:00.00) | End: (00:08.00)
"This wasn't a street mugging. This military-grade neural lace was ripped out clean."

**KIRA (Tense):**
Start: (00:08.00) | End: (00:25.00)
"Silas, drop the badge. Syndicate leader Vance ordered everyone who saw this code silenced."

**SILAS (Steely):**
Start: (00:25.00) | End: (00:45.00)
"Tell Vance I am coming for his server farm next."

--- SCRIPT END ---
"""

DIFF_THEMED_EP2 = """EPISODE NUMBER: 2
EPISODE LOGLINE: Silas storms the neon district to extract an encrypted memory core.

SCENE 1
Scene heading: INT. NEON CLUB - NIGHT
Scene start: 00:00.00
Scene end: 00:50.00

**VANCE (Smirking):**
Start: (00:00.00) | End: (00:10.00)
"You walked right into the kill zone, Detective."

**SILAS (Deadly):**
Start: (00:10.00) | End: (00:30.00)
"I didn't come to arrest you. I came to shut down your black market rig."

**VANCE (Laughing):**
Start: (00:30.00) | End: (00:50.00)
"The virus is already pulsing through the city grid. You are ten seconds too late."

--- SCRIPT END ---
"""

DIFF_THEMED_EP3 = """EPISODE NUMBER: 3
EPISODE LOGLINE: The blackout hits Neo-Veridia as Silas makes a desperate choice.

SCENE 1
Scene heading: EXT. ROOFTOP RELAY - DAWN
Scene start: 00:00.00
Scene end: 00:40.00

**KIRA (Screaming):**
Start: (00:00.00) | End: (00:08.00)
"Cut the main uplink or the entire sector goes dark!"

**SILAS (Resolute):**
Start: (00:08.00) | End: (00:28.00)
"If I pull this relay, my own neural heart stops beating."

**KIRA (Desperate):**
Start: (00:28.00) | End: (00:40.00)
"Silas, don't do it!"

--- SCRIPT END ---
"""


class MockCyberpunkProvider(BaseLLMProvider):
    @property
    def name(self) -> str:
        return "mock_cyber"

    @property
    def model(self) -> str:
        return "cyber-model"

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        profile_yaml = """show_title: "Neon Shroud"
premise: "In a neon-drenched dystopian metropolis, rogue detective Silas Ray battles syndicate boss Vance to stop a lethal neural virus before the city falls into perpetual darkness."
target_platform: "TikTok / Instagram Reels"
protagonist:
  name: "Detective Silas Ray"
  archetype: "Cynical cybernetic detective with a ticking neural clock"
  core_conflict: "Exposing corporate syndicate crime while keeping his failing cyberware alive."
male_lead:
  name: "Silas Ray"
  role: "Hardboiled investigator"
antagonists:
  - name: "Vance"
    role: "Ruthless syndicate boss running the black-market neural trade"
recurring_settings:
  - "Neo-Veridia lower alleyways"
  - "The Neon Club black site"
  - "The Rooftop Transmission Relay"
"""
        return {"profile_yaml": profile_yaml}


class TestAutoProfile(unittest.TestCase):
    def test_compare_generated_profile_with_handwritten(self):
        """
        Tests generated profile against the hand-written profile:
        reports matched facts, wrong facts, and missing facts.
        """
        handwritten_path = Path("config/shows/broken_soldier.yaml")
        generated_path = Path("config/shows/broken_soldier.generated.yaml")

        self.assertTrue(handwritten_path.exists(), "Handwritten profile must exist")
        self.assertTrue(generated_path.exists(), "Generated profile must exist from Stage D")

        hw = yaml.safe_load(handwritten_path.read_text())
        gen = yaml.safe_load(generated_path.read_text())

        matched_facts = []
        wrong_facts = []
        missing_facts = []

        # Protagonist check
        hw_prot = hw.get("protagonist", {}).get("name", "")
        gen_prot = gen.get("protagonist", {}).get("name", "")
        if "Juliana" in gen_prot and "Juliana" in hw_prot:
            matched_facts.append(f"Protagonist name matched: '{gen_prot}' contains '{hw_prot}'")
        else:
            wrong_facts.append(f"Protagonist mismatch: HW='{hw_prot}', Gen='{gen_prot}'")

        # Male lead check
        hw_ml = hw.get("male_lead", {}).get("name", "")
        gen_ml = gen.get("male_lead", {}).get("name", "")
        if "Alexander" in gen_ml:
            matched_facts.append(f"Male lead matched: '{gen_ml}'")
        else:
            wrong_facts.append(f"Male lead mismatch: HW='{hw_ml}', Gen='{gen_ml}'")

        # Antagonists check
        hw_ants = [a.get("name", "") for a in hw.get("antagonists", []) if a.get("name")]
        gen_ants = [a.get("name", "") for a in gen.get("antagonists", []) if a.get("name")]
        matched_ant_pairs = []
        for h in hw_ants:
            match = next((g for g in gen_ants if h.lower() in g.lower() or g.lower() in h.lower() or (h == "Matriarch" and "lady ashcroft" in g.lower())), None)
            if match:
                matched_ant_pairs.append((h, match))

        matched_facts.append(f"Antagonists matched: {matched_ant_pairs}")
        missing_ants = [h for h in hw_ants if not any(h == pair[0] for pair in matched_ant_pairs)]
        if missing_ants:
            missing_facts.append(f"Antagonists in handwritten but missing in generated: {missing_ants}")

        # Title check
        hw_title = hw.get("show_title", "")
        gen_title = gen.get("show_title", "")
        if hw_title.lower() != gen_title.lower():
            wrong_facts.append(f"Show title divergence: HW='{hw_title}', Gen='{gen_title}'")
        else:
            matched_facts.append("Show title exact match")

        # Missing Duke secret identity in title
        if "duke" not in gen_title.lower():
            missing_facts.append("Generated title misses explicit 'He was a Duke' secret identity label")

        print("\n=== AUTO-PROFILE FACT COMPARISON REPORT ===")
        print(f"Matched facts ({len(matched_facts)}):")
        for m in matched_facts:
            print(f"  ✓ {m}")
        print(f"Wrong/divergent facts ({len(wrong_facts)}):")
        for w in wrong_facts:
            print(f"  ✗ {w}")
        print(f"Missing facts ({len(missing_facts)}):")
        for mis in missing_facts:
            print(f"  ? {mis}")

        # Assert key entities were identified
        self.assertIn("Juliana", gen_prot)
        self.assertIn("Alexander", gen_ml)
        self.assertTrue(len(matched_ant_pairs) >= 2, "At least 2 core antagonists matched")

    def test_auto_profile_on_custom_cyberpunk_screenplay(self):
        """Tests auto-profile generation on a differently themed 3-episode cyberpunk screenplay."""
        ep1 = parse_screenplay_text(DIFF_THEMED_EP1, "cyber-001.txt")
        ep2 = parse_screenplay_text(DIFF_THEMED_EP2, "cyber-002.txt")
        ep3 = parse_screenplay_text(DIFF_THEMED_EP3, "cyber-003.txt")
        cyber_episodes = [ep1, ep2, ep3]

        prov = MockCyberpunkProvider()
        with tempfile.NamedTemporaryFile(suffix=".generated.yaml", delete=False) as f:
            out_path = f.name

        try:
            profile = run_auto_profile(cyber_episodes, "neon_shroud", out_path, prov)
            self.assertEqual(profile["show_title"], "Neon Shroud")
            self.assertIn("Silas", profile["protagonist"]["name"])
            self.assertIn("Vance", [a["name"] for a in profile["antagonists"]])
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as pf:
                loaded = yaml.safe_load(pf.read())
            self.assertEqual(loaded["show_title"], "Neon Shroud")
        finally:
            if os.path.exists(out_path):
                os.remove(out_path)


if __name__ == "__main__":
    unittest.main()
