"""
Test integration for eval/verify_claims.py.
Ensures that all claims in SOLUTION_DOC.md, README.md, and AGENTS.md match committed outputs.
"""

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from eval.verify_claims import compute_ground_truth_metrics, verify_file_claims, ROOT


class TestVerifyClaims(unittest.TestCase):
    def test_claims_across_docs_match_committed_outputs(self):
        """Recomputes metrics from committed outputs and asserts 0 mismatches across documentation."""
        metrics = compute_ground_truth_metrics()

        docs = [
            ROOT / "SOLUTION_DOC.md",
            ROOT / "README.md",
            ROOT / "AGENTS.md",
        ]

        all_issues = []
        for doc in docs:
            if doc.exists():
                issues = verify_file_claims(doc, metrics)
                all_issues.extend(issues)

        if all_issues:
            self.fail(f"Claims mismatch detected:\n" + "\n".join(all_issues))

    def test_virality_fails_verification(self):
        """Asserts that verify_file_claims fails if 'virality' or 'A-grade' is present in a file."""
        import tempfile
        metrics = compute_ground_truth_metrics()
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Doc\nPredicting virality score for promos.\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            issues = verify_file_claims(temp_path, metrics)
            self.assertTrue(any("virality" in iss for iss in issues), f"Expected virality issue, got {issues}")
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
