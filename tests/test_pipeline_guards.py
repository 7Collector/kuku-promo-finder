"""Provider factory, auditor strictness, ranking gate, parser failure modes."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.auditor import PromoAuditor, parse_bool, normalize_flaw
from src.models import (CliffhangerInfo, HookInfo, PromoCandidate, PromoScores, QualityAudit, Segment)
from src.parser import parse_all_episodes
from src.providers.factory import ProviderConfigError, get_llm_provider
from src.providers.http import ProviderError, scrub
from src.providers.resilience import RetryingProvider
from src.ranker import PromoRanker
from src.taxonomy import Taxonomy


def cand(pid, ep, score, passed=None, flaw=None):
    c = PromoCandidate(
        promo_id=pid, episodes=[ep],
        segments=[Segment(episode=ep, start="00:00.00", end="00:30.00", start_seconds=0, end_seconds=30)],
        hook=HookInfo(type="public_humiliation", timestamp="00:00.00", timestamp_seconds=0, quote="q"),
        cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:30.00", timestamp_seconds=30, quote="q"),
        scores=PromoScores(composite_score=score),
    )
    if passed is not None:
        c.quality_audit = QualityAudit(passed=passed, flaw_type=flaw, method="llm")
    return c


class TestGuards(unittest.TestCase):
    def test_unknown_provider_raises(self):
        with self.assertRaises(ProviderConfigError):
            get_llm_provider("bogus")

    def test_missing_key_raises_instead_of_heuristic(self):
        saved = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with self.assertRaises(ProviderConfigError):
                get_llm_provider("anthropic")
        finally:
            if saved:
                os.environ["ANTHROPIC_API_KEY"] = saved

    def test_string_false_is_false(self):
        self.assertFalse(parse_bool("false"))
        self.assertTrue(parse_bool("true"))
        with self.assertRaises(ValueError):
            parse_bool("maybe")

    def test_free_text_flaw_maps_to_enum(self):
        self.assertEqual(normalize_flaw("Resolution Leak: conflict resolved"), "resolution_leak")
        self.assertEqual(normalize_flaw("needs backstory (context)"), "context_deficit")
        self.assertIsNone(normalize_flaw(None))

    def test_failed_llm_audit_is_marked_unaudited_not_rule_passed(self):
        mock = MagicMock()
        mock.name, mock.model, mock.is_live = "m", "m1", True
        mock.generate_json.side_effect = ProviderError("boom")
        audit = PromoAuditor(llm_provider=mock).audit_candidate(cand("a", 1, 8))
        self.assertEqual(audit.method, "error")
        self.assertFalse(audit.passed)

    def test_every_pass_outranks_every_fail(self):
        fail_hi = cand("fail_hi", 1, 9.9, passed=False, flaw="other")
        pass_lo = cand("pass_lo", 2, 6.0, passed=True)
        ranked = PromoRanker(Taxonomy("config/taxonomy.yaml")).rerank_for_diversity([fail_hi, pass_lo], top_k=2)
        self.assertEqual([c.promo_id for c in ranked], ["pass_lo", "fail_hi"])

    def test_dedup_ignores_clock_overlap_across_episodes(self):
        r = PromoRanker(Taxonomy("config/taxonomy.yaml"))
        a, b = cand("a", 1, 9), cand("b", 2, 8)
        self.assertEqual(len(r.deduplicate([a, b])), 2)
        c = cand("c", 1, 7)
        self.assertEqual(len(r.deduplicate([a, c])), 1)

    def test_retry_gives_up_on_non_retryable(self):
        inner = MagicMock()
        inner.name, inner.model, inner.is_live = "m", "m1", True
        inner.generate_json.side_effect = ProviderError("HTTP 401", status=401, retryable=False)
        with self.assertRaises(ProviderError):
            RetryingProvider(inner, attempts=3, base_delay=0).generate_json("s", "u")
        self.assertEqual(inner.generate_json.call_count, 1)

    def test_secret_is_scrubbed(self):
        self.assertNotIn("KEY123", scrub("bad url ?key=KEY123", "KEY123"))

    def test_parser_fails_loudly_on_bad_input(self):
        with self.assertRaises(FileNotFoundError):
            parse_all_episodes("/nonexistent/dir")
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "episode-001.txt"), "w").write("00:00:11,300 --> 00:00:13,000\nhello\n")
            self.assertEqual(parse_all_episodes(d), [])


if __name__ == "__main__":
    unittest.main()
