"""
Unit tests for screenplay parser.
"""

import os
from src.parser import parse_screenplay_file, parse_all_episodes, format_episode_for_analysis
from src.models import BeatType


def test_parser():
    script_dir = "assets/I Married a Broken Soldier. He was a Duke"
    episodes = parse_all_episodes(script_dir)
    
    assert len(episodes) == 50, f"Expected 50 episodes, got {len(episodes)}"
    
    # Check Episode 1
    ep1 = episodes[0]
    assert ep1.episode_number == 1
    assert "altar" in ep1.logline.lower() or "betrayal" in ep1.logline.lower()
    assert len(ep1.scenes) >= 1
    assert ep1.total_duration > 60.0
    
    # Verify beats
    all_beats = ep1.all_beats
    assert len(all_beats) > 20
    dialogue_beats = [b for b in all_beats if b.beat_type == BeatType.DIALOGUE]
    assert len(dialogue_beats) > 5
    
    # Check text formatting
    formatted = format_episode_for_analysis(ep1, include_camera=False)
    assert "EPISODE 1:" in formatted
    assert "Gerald" in formatted or "Juliana" in formatted

    print(f"Parser tests passed successfully! Parsed {len(episodes)} episodes.")


if __name__ == "__main__":
    test_parser()
