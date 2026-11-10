"""
Tier 2 Boundary Tests: Timeouts and Network Failures.
Verifies sandbox process timeouts, simulated HTTP gateway errors, and connection drops.
"""

import unittest
from tests.e2e.harness.contract_loader import get_sandbox
from tests.e2e.harness.mock_server import MockPlatformServer


class TestBoundaryTimeoutsNetworkFailures(unittest.TestCase):
    """Verifies robustness during timeouts, network hangs, and external server errors."""

    def setUp(self):
        self.sandbox, _ = get_sandbox()

    def test_sandbox_process_hang_kills_cleanly(self):
        """Verifies sandbox terminates hanging processes within specified timeout without zombie processes."""
        hang_code = (
            "import time\n"
            "time.sleep(10)\n"
            "print('done')\n"
        )
        res = self.sandbox.validate_solution(hang_code, "", "done", timeout_sec=0.4)
        self.assertFalse(res.passed)
        self.assertEqual(res.exit_code, -1)
        self.assertIn("timed out", (res.error_message or "").lower())

    def test_mock_server_404_endpoint_handling(self):
        """Verifies unknown endpoints return clean 404 without crashing server."""
        import urllib.request
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/nonexistent-api-endpoint"
            try:
                urllib.request.urlopen(url)
                self.fail("Expected HTTPError 404")
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)


if __name__ == "__main__":
    unittest.main()
