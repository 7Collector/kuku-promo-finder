"""
Unit tests for screenplay parser.
"""

import unittest
from src.parser import parse_screenplay_text, parse_all_episodes
from src.models import BeatType


class TestScreenplayParser(unittest.TestCase):
    def test_parse_with_and_without_parentheses(self):
        sample_script = """EPISODE NUMBER: Episode 99
EPISODE LOGLINE: Test logline for unit verification.
CONTINUITY NOTES: Test notes.

--- SCRIPT START ---

SCENE 01
Scene heading: INT. ROOM - DAY
Scene start: 00:00.00
Scene end: 01:00.00

Actions and dialogue:

**CAMERA:**
Start: 00:00.00 | End: 00:04.00
Wide shot of room without parentheses.

**JULIANA (Furious):**
Start: (00:04.00) | End: (00:08.50)
"How dare you betray me!"

**ACTION:**
Start: 00:08.50 | End: 00:12.00
She slams the ring onto the mahogany table.
"""
        ep = parse_screenplay_text(sample_script, filename="test_ep.txt")
        self.assertEqual(ep.episode_number, 99)
        self.assertEqual(len(ep.scenes), 1)
        self.assertEqual(len(ep.all_beats), 3)

        b_cam = ep.all_beats[0]
        self.assertEqual(b_cam.beat_type, BeatType.CAMERA)
        self.assertEqual(b_cam.start_seconds, 0.0)
        self.assertEqual(b_cam.end_seconds, 4.0)

        b_dia = ep.all_beats[1]
        self.assertEqual(b_dia.beat_type, BeatType.DIALOGUE)
        self.assertEqual(b_dia.speaker, "JULIANA")
        self.assertEqual(b_dia.emotion, "Furious")
        self.assertEqual(b_dia.start_seconds, 4.0)
        self.assertEqual(b_dia.end_seconds, 8.5)

    def test_parse_assets_pack(self):
        episodes = parse_all_episodes("assets/I Married a Broken Soldier. He was a Duke")
        self.assertEqual(len(episodes), 50)
        self.assertEqual(episodes[0].episode_number, 1)
        self.assertGreater(len(episodes[0].all_beats), 20)


if __name__ == "__main__":
    unittest.main()
