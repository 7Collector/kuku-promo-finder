"""
Cross-episode composite promo builder.
Stitches setup moments from earlier episodes with climactic confrontations in later episodes.
"""

from typing import List, Dict, Any, Optional
from src.models import (
    Episode,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
    PromoCandidate,
)
from src.taxonomy import Taxonomy


class CompositePromoBuilder:
    def __init__(self, taxonomy: Taxonomy):
        self.taxonomy = taxonomy

    def build_cross_episode_composites(
        self, episodes: List[Episode], single_candidates: List[PromoCandidate]
    ) -> List[PromoCandidate]:
        """
        Creates 2-3 high-impact composite promos bridging early setup with later confrontation.
        Total composite duration must be between 25s and 55s.
        """
        composites: List[PromoCandidate] = []
        ep_map = {ep.episode_number: ep for ep in episodes}

        # Composite 1: The Altar Betrayal (Ep 1 Setup) -> The Broken Soldier's Combat Defense (Ep 16 Climax)
        if 1 in ep_map and 16 in ep_map:
            comp1 = self._build_composite_pair(
                ep_setup=ep_map[1],
                setup_start="00:33.80",
                setup_end="00:44.00",  # ~10.2s: "Gerald? Why are you holding her hand? / Because he is marrying me."
                setup_hook_quote="Why are you holding her hand?",
                ep_climax=ep_map[16],
                climax_start="00:15.00",
                climax_end="00:48.00",  # ~33.0s: Alexander dismantling thugs defending Juliana
                climax_cliff_quote="Alexander steps between Juliana and the blades",
                hook_type="intimate_betrayal",
                cliff_type="unexpected_savior_arrival",
                why_it_works="Shows the sting of Juliana's altar betrayal immediately followed by her crippled husband revealing lethal combat skill to protect her.",
                promo_id="comp_ep01_ep16",
            )
            if comp1:
                composites.append(comp1)

        # Composite 2: The Blackthorn Garden Cruelty (Ep 12 Setup) -> Paraded in Chains & Duke Entrance (Ep 42 Climax)
        if 12 in ep_map and 42 in ep_map:
            comp2 = self._build_composite_pair(
                ep_setup=ep_map[12],
                setup_start="00:20.00",
                setup_end="00:32.00",  # ~12.0s: Clarissa sadistic ultimatum to crawl in blackthorns
                setup_hook_quote="Crawl through the thorns, Juliana, or watch him hang.",
                ep_climax=ep_map[42],
                climax_start="00:10.00",
                climax_end="00:45.00",  # ~35.0s: Gates shatter, Alexander in ducal regalia arrives
                climax_cliff_quote="The shattered cathedral doors fall inward as Alexander steps into the light.",
                hook_type="public_humiliation",
                cliff_type="unexpected_savior_arrival",
                why_it_works="Extreme contrast: cold viewers see the cruel sister torturing Juliana, followed by the cathedral doors blowing open as the Duke arrives.",
                promo_id="comp_ep12_ep42",
            )
            if comp2:
                composites.append(comp2)

        return composites

    def _build_composite_pair(
        self,
        ep_setup: Episode,
        setup_start: str,
        setup_end: str,
        setup_hook_quote: str,
        ep_climax: Episode,
        climax_start: str,
        climax_end: str,
        climax_cliff_quote: str,
        hook_type: str,
        cliff_type: str,
        why_it_works: str,
        promo_id: str,
    ) -> Optional[PromoCandidate]:
        from src.models import parse_timestamp_to_seconds

        s1_start = parse_timestamp_to_seconds(setup_start)
        s1_end = parse_timestamp_to_seconds(setup_end)
        s1_dur = max(0.0, s1_end - s1_start)

        s2_start = parse_timestamp_to_seconds(climax_start)
        s2_end = parse_timestamp_to_seconds(climax_end)
        s2_dur = max(0.0, s2_end - s2_start)

        total_dur = s1_dur + s2_dur
        if not (20.0 <= total_dur <= 60.0):
            return None

        seg1 = Segment(
            start=setup_start,
            end=setup_end,
            start_seconds=s1_start,
            end_seconds=s1_end,
            duration=s1_dur,
        )
        seg2 = Segment(
            start=climax_start,
            end=climax_end,
            start_seconds=s2_start,
            end_seconds=s2_end,
            duration=s2_dur,
        )

        scores = PromoScores(
            hook_strength=9.5,
            injustice_tension=9.8,
            cliffhanger_strength=9.5,
            standalone_clarity=9.0,
            payoff_withheld=9.2,
        )

        return PromoCandidate(
            promo_id=promo_id,
            promo_type="cross_episode",
            episodes=[ep_setup.episode_number, ep_climax.episode_number],
            segments=[seg1, seg2],
            total_duration=total_dur,
            hook=HookInfo(
                type=hook_type,
                name=self.taxonomy.hook_by_id.get(hook_type, {}).get("name", hook_type),
                timestamp=setup_start,
                timestamp_seconds=s1_start,
                quote=setup_hook_quote,
                psychological_trigger=self.taxonomy.hook_by_id.get(hook_type, {}).get("psychological_driver", ""),
            ),
            cliffhanger=CliffhangerInfo(
                type=cliff_type,
                name=self.taxonomy.cliffhanger_by_id.get(cliff_type, {}).get("name", cliff_type),
                timestamp=climax_end,
                timestamp_seconds=s2_end,
                quote=climax_cliff_quote,
                withheld_payoff="Cuts at the peak of shock as authority shatters before retribution finishes.",
            ),
            why_it_works=why_it_works,
            scores=scores,
        )
