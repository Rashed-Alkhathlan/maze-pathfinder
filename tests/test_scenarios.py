import importlib.util
import unittest

from src.scenarios import SCENARIOS, all_scenarios, get_scenario

FASTAPI_READY = bool(importlib.util.find_spec("fastapi")) and bool(importlib.util.find_spec("httpx"))


class ScenarioDefinitionTests(unittest.TestCase):
    def test_all_twelve_scenarios_defined(self) -> None:
        self.assertEqual(len(SCENARIOS), 12)

    def test_get_scenario_returns_expected_keys(self) -> None:
        scenario = get_scenario("DFS", "worst")
        for key in ("size", "seed", "weighted", "loop_factor", "description"):
            self.assertIn(key, scenario)

    def test_get_scenario_raises_on_invalid(self) -> None:
        with self.assertRaises(ValueError):
            get_scenario("INVALID", "best")

    def test_all_scenarios_returns_list_of_dicts(self) -> None:
        result = all_scenarios()
        self.assertEqual(len(result), 12)
        for item in result:
            self.assertIn("algorithm", item)
            self.assertIn("case", item)


class ScenarioRunTests(unittest.TestCase):
    """Run each curated scenario and verify the results match expectations."""

    def test_dfs_best_matches_bfs_path_length(self) -> None:
        from src.comparison import run_single_seed

        s = get_scenario("DFS", "best")
        payload = run_single_seed(size=s["size"], seed=s["seed"], weighted=s["weighted"], loop_factor=s["loop_factor"])
        dfs = next(a for a in payload["algorithms"] if a["algorithm"] == "DFS")
        bfs = next(a for a in payload["algorithms"] if a["algorithm"] == "BFS")
        self.assertEqual(dfs["metrics"]["path_length"], bfs["metrics"]["path_length"])

    def test_dfs_worst_inflates_path(self) -> None:
        from src.comparison import run_single_seed

        s = get_scenario("DFS", "worst")
        payload = run_single_seed(size=s["size"], seed=s["seed"], weighted=s["weighted"], loop_factor=s["loop_factor"])
        dfs = next(a for a in payload["algorithms"] if a["algorithm"] == "DFS")
        bfs = next(a for a in payload["algorithms"] if a["algorithm"] == "BFS")
        self.assertGreater(dfs["metrics"]["path_length"], bfs["metrics"]["path_length"] * 2)

    def test_bfs_worst_overpays_dijkstra(self) -> None:
        from src.comparison import run_single_seed

        s = get_scenario("BFS", "worst")
        payload = run_single_seed(size=s["size"], seed=s["seed"], weighted=s["weighted"], loop_factor=s["loop_factor"])
        bfs = next(a for a in payload["algorithms"] if a["algorithm"] == "BFS")
        dijkstra = next(a for a in payload["algorithms"] if a["algorithm"] == "Dijkstra")
        self.assertGreater(bfs["metrics"]["path_cost"], dijkstra["metrics"]["path_cost"] * 1.5)

    def test_astar_best_explores_fewer_than_dijkstra(self) -> None:
        from src.comparison import run_single_seed

        s = get_scenario("A*", "best")
        payload = run_single_seed(size=s["size"], seed=s["seed"], weighted=s["weighted"], loop_factor=s["loop_factor"])
        astar = next(a for a in payload["algorithms"] if a["algorithm"] == "A*")
        dijkstra = next(a for a in payload["algorithms"] if a["algorithm"] == "Dijkstra")
        self.assertLess(astar["metrics"]["nodes_explored"], dijkstra["metrics"]["nodes_explored"] * 0.6)

    def test_astar_worst_matches_dijkstra_explored(self) -> None:
        from src.comparison import run_single_seed

        s = get_scenario("A*", "worst")
        payload = run_single_seed(size=s["size"], seed=s["seed"], weighted=s["weighted"], loop_factor=s["loop_factor"])
        astar = next(a for a in payload["algorithms"] if a["algorithm"] == "A*")
        dijkstra = next(a for a in payload["algorithms"] if a["algorithm"] == "Dijkstra")
        self.assertEqual(astar["metrics"]["nodes_explored"], dijkstra["metrics"]["nodes_explored"])


@unittest.skipUnless(FASTAPI_READY, "fastapi and httpx are required for API tests")
class ScenarioApiTests(unittest.TestCase):
    def test_get_scenarios_returns_12(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        client = TestClient(app)
        response = client.get("/api/scenarios")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 12)

    def test_run_scenario_returns_valid_payload(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        client = TestClient(app)
        response = client.post("/api/scenarios/run", json={"algorithm": "DFS", "case": "worst"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("seed", payload)
        self.assertIn("maze", payload)
        self.assertIn("algorithms", payload)
        self.assertEqual(len(payload["algorithms"]), 4)

    def test_batch_endpoint_returns_averaged_metrics(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        client = TestClient(app)
        response = client.post("/api/batch", json={"size": 8, "count": 3})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 3)
        self.assertEqual(len(data["algorithms"]), 4)
        for alg in data["algorithms"]:
            self.assertIn("algorithm", alg)
            for key in ("nodes_explored", "runtime_ms", "path_length", "path_cost"):
                self.assertIn("mean", alg[key])
                self.assertIn("min", alg[key])
                self.assertIn("max", alg[key])


if __name__ == "__main__":
    unittest.main()
