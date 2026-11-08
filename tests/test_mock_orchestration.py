"""
Tests for mock provider with slow responses and HTTP 429 rate limiting.
Ensures orchestration completes with retry or reports failed episodes honestly.
"""

import time
import unittest


class MockProviderClient:
    def __init__(self, fail_with_429_until=0, latency_seconds=0.0):
        self.fail_with_429_until = fail_with_429_until
        self.latency_seconds = latency_seconds
        self.call_count = 0

    def call_api(self, payload):
        self.call_count += 1
        if self.latency_seconds > 0:
            time.sleep(self.latency_seconds)

        if self.call_count <= self.fail_with_429_until:
            return {"status": 429, "error": "Rate limit exceeded"}

        return {"status": 200, "data": {"candidates": [{"id": f"cand_{self.call_count}"}]}}


def orchestrate_episode_extraction(episodes, client, max_retries=3, backoff_base=0.01):
    valid_candidates = []
    failed_episodes = []

    for ep in episodes:
        attempt = 0
        success = False
        last_error = None

        while attempt <= max_retries:
            res = client.call_api(ep)
            if res["status"] == 200:
                valid_candidates.extend(res["data"]["candidates"])
                success = True
                break
            elif res["status"] == 429:
                attempt += 1
                last_error = res["error"]
                if attempt <= max_retries:
                    # Exponential backoff simulation
                    time.sleep(backoff_base * (2 ** attempt))
            else:
                last_error = res.get("error", "Unknown error")
                break

        if not success:
            failed_episodes.append({
                "episode_number": ep.get("number", 0),
                "error": last_error,
            })

    return {
        "candidates": valid_candidates,
        "failed_episodes": failed_episodes,
    }


class TestMockOrchestration(unittest.TestCase):
    def test_mock_provider_slow_completes(self):
        """Slow provider (e.g. 50ms latency per request) successfully completes all episodes."""
        client = MockProviderClient(latency_seconds=0.02)
        episodes = [{"number": 1}, {"number": 2}, {"number": 3}]

        start_t = time.time()
        result = orchestrate_episode_extraction(episodes, client)
        duration = time.time() - start_t

        self.assertEqual(len(result["candidates"]), 3)
        self.assertEqual(len(result["failed_episodes"]), 0)
        self.assertGreaterEqual(duration, 0.05)

    def test_mock_provider_429_retries_and_succeeds(self):
        """Provider returns 429 twice, then succeeds on retry 3."""
        client = MockProviderClient(fail_with_429_until=2)
        episodes = [{"number": 1}]

        result = orchestrate_episode_extraction(episodes, client, max_retries=3, backoff_base=0.005)

        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(len(result["failed_episodes"]), 0)
        self.assertEqual(client.call_count, 3)

    def test_mock_provider_429_exhausted_reports_failed_never_empty(self):
        """Provider repeatedly returns 429; episode is reported as failed, never empty or passed."""
        client = MockProviderClient(fail_with_429_until=999)
        episodes = [{"number": 5}]

        result = orchestrate_episode_extraction(episodes, client, max_retries=2, backoff_base=0.005)

        self.assertEqual(len(result["candidates"]), 0)
        self.assertEqual(len(result["failed_episodes"]), 1)
        self.assertEqual(result["failed_episodes"][0]["episode_number"], 5)
        self.assertEqual(result["failed_episodes"][0]["error"], "Rate limit exceeded")


if __name__ == "__main__":
    unittest.main()
