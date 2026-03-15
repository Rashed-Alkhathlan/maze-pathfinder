import importlib.util
import unittest


FASTAPI_READY = bool(importlib.util.find_spec("fastapi")) and bool(importlib.util.find_spec("httpx"))


@unittest.skipUnless(FASTAPI_READY, "fastapi and httpx are required for API tests")
class ApiTests(unittest.TestCase):
    def test_run_endpoint_returns_maze_and_algorithm_payloads(self) -> None:
        from fastapi.testclient import TestClient

        from src.app import app

        client = TestClient(app)
        response = client.post(
            "/api/run",
            json={"size": 7, "seed": 123, "weighted": True, "loop_factor": 0.2},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["seed"], 123)
        self.assertEqual(payload["maze"]["grid_size"], 15)
        self.assertTrue(payload["maze"]["weighted"])
        self.assertAlmostEqual(payload["maze"]["loop_factor"], 0.2)
        self.assertEqual([item["algorithm"] for item in payload["algorithms"]], ["BFS", "DFS", "Dijkstra", "A*"])

        expected_metric_keys = {"nodes_explored", "frontier_peak", "path_length", "path_cost", "runtime_ms"}
        for item in payload["algorithms"]:
            self.assertIn("events", item)
            self.assertIn("metrics", item)
            self.assertIn("status", item)
            self.assertIn("actual_optimal", item)
            self.assertIn("optimality_note", item)
            self.assertEqual(set(item["metrics"].keys()), expected_metric_keys)

        dijkstra = next(item for item in payload["algorithms"] if item["algorithm"] == "Dijkstra")
        self.assertTrue(dijkstra["actual_optimal"])


if __name__ == "__main__":
    unittest.main()
