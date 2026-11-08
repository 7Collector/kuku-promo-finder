"""
Unit tests for Gemini judge:
- Request and response parsing
- Malformed JSON handling (retries once, then audit_error)
- audit_error never passes
- Refuse-same-model rule
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from src.models import (
    PromoCandidate,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
    QualityAudit,
)
from src.taxonomy import Taxonomy
from src.providers.base import BaseLLMProvider
from src.providers.gemini import GeminiProvider
from src.providers.http import ProviderError
from src.auditor import PromoAuditor
from src.ranker import PromoRanker
from run import run_pipeline, PipelineError


class FakeGeminiResponse:
    def __init__(self, data: dict, status_code: int = 200, text: str = ""):
        self._data = data
        self.status_code = status_code
        self.text = text or json.dumps(data)

    def json(self):
        return self._data


class TestGeminiJudge(unittest.TestCase):
    def test_gemini_request_and_response_parsing(self):
        """Tests that GeminiProvider builds proper payload and parses candidates & usage."""
        fake_api_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "passes_editorial_standard": True,
                                    "flaw_type": None,
                                    "critique": "Solid cold hook with clear stakes and high conversion.",
                                    "confidence_score": 9.0,
                                    "conversion_intent": 8.5,
                                    "editorial_risks": [],
                                })
                            }
                        ]
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 120,
                "candidatesTokenCount": 60,
                "thoughtsTokenCount": 0,
            },
        }

        with patch("src.providers.gemini.discover_gemini_flash_model", return_value="gemini-2.5-flash"):
            with patch("src.providers.http.requests.post") as mock_post:
                mock_post.return_value = FakeGeminiResponse(fake_api_response)
                provider = GeminiProvider(api_key="test-gemini-key")
                self.assertEqual(provider.model, "gemini-2.5-flash")

                res = provider.generate_json("System prompt", "User prompt")
                self.assertTrue(res["passes_editorial_standard"])
                self.assertEqual(res["confidence_score"], 9.0)
                self.assertEqual(res["conversion_intent"], 8.5)
                self.assertEqual(provider.usage["prompt_tokens"], 120)
                self.assertEqual(provider.usage["completion_tokens"], 60)

                # Verify payload structure sent to Gemini API
                call_args, call_kwargs = mock_post.call_args
                payload = call_kwargs["json"]
                self.assertIn("systemInstruction", payload)
                self.assertIn("contents", payload)
                self.assertEqual(payload["contents"][0]["role"], "user")
                self.assertEqual(payload["generationConfig"]["responseMimeType"], "application/json")

    def test_malformed_json_retries_once_then_audit_error(self):
        """On malformed JSON response, retries once, then marks candidate unaudited with audit_error."""
        bad_response = {
            "candidates": [
                {"content": {"parts": [{"text": "{ not valid json ..."}]}}
            ],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 10},
        }

        with patch("src.providers.gemini.discover_gemini_flash_model", return_value="gemini-2.5-flash"):
            with patch("src.providers.http.requests.post") as mock_post:
                mock_post.return_value = FakeGeminiResponse(bad_response)
                provider = GeminiProvider(api_key="test-gemini-key")
                auditor = PromoAuditor(llm_provider=provider)

                cand = PromoCandidate(
                    promo_id="ep01_test",
                    episodes=[1],
                    segments=[Segment(episode=1, start="00:00.00", end="00:30.00", start_seconds=0.0, end_seconds=30.0)],
                    hook=HookInfo(type="public_humiliation", timestamp="00:00.00", timestamp_seconds=0.0, quote="Test hook"),
                    cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:30.00", timestamp_seconds=30.0, quote="Test cliff"),
                    scores=PromoScores(),
                )

                audit = auditor.audit_candidate(cand)
                self.assertFalse(audit.passed)
                self.assertEqual(audit.method, "error")
                self.assertEqual(audit.flaw_type, "audit_error")
                self.assertIn("Audit unavailable", audit.critique)

    def test_audit_error_never_passes(self):
        """Candidates with method='error' or flaw_type='audit_error' are never marked passed or included in top 15."""
        cand = PromoCandidate(
            promo_id="ep01_err",
            episodes=[1],
            segments=[Segment(episode=1, start="00:00.00", end="00:30.00", start_seconds=0.0, end_seconds=30.0)],
            hook=HookInfo(type="public_humiliation", timestamp="00:00.00", timestamp_seconds=0.0, quote="Test hook"),
            cliffhanger=CliffhangerInfo(type="mortal_ultimatum", timestamp="00:30.00", timestamp_seconds=30.0, quote="Test cliff"),
            scores=PromoScores(composite_score=9.5),
            quality_audit=QualityAudit(passed=False, method="error", flaw_type="audit_error", critique="API 500"),
        )
        self.assertFalse(cand.quality_audit.passed)

        ranker = PromoRanker(Taxonomy("config/taxonomy.yaml"))
        ranked = ranker.rerank_for_diversity([cand], top_k=5)
        # Excluded from top selection
        self.assertEqual(len(ranked), 0)

    def test_refuse_same_model_rule(self):
        """Pipeline refuses to run when extractor model == only judge unless --allow-self-audit is passed."""
        # When extractor and judge are both openai:gpt-6-luna without allow_self_audit:
        with patch("run.get_llm_provider") as mock_get_provider:
            fake_provider = MagicMock(spec=BaseLLMProvider)
            fake_provider.name = "openai"
            fake_provider.model = "gpt-6-luna"
            fake_provider.is_live = True
            fake_provider.usage = {"calls": 1, "cache_hits": 0, "prompt_tokens": 10, "completion_tokens": 10}
            mock_get_provider.return_value = fake_provider

            with self.assertRaises(PipelineError) as ctx:
                run_pipeline(
                    input_dir="assets/I Married a Broken Soldier. He was a Duke",
                    taxonomy_path="config/taxonomy.yaml",
                    context_path="config/shows/broken_soldier.yaml",
                    output_json="/tmp/test_promos.json",
                    output_md="/tmp/test_promos.md",
                    provider="openai",
                    model="gpt-6-luna",
                    audit_provider="openai",
                    audit_model="gpt-6-luna",
                    allow_self_audit=False,
                )
            self.assertIn("cannot be the sole auditor without --allow-self-audit", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
