import unittest

from src.comparison import run_algorithm_suite


class ComparisonTests(unittest.TestCase):
    def test_run_algorithm_suite_is_deterministic_for_same_seed(self) -> None:
        first = run_algorithm_suite(size=12, seed=1234, weighted=True, loop_factor=0.18)
        second = run_algorithm_suite(size=12, seed=1234, weighted=True, loop_factor=0.18)

        self.assertEqual(first["seed"], second["seed"])
        self.assertEqual(first["maze"]["grid"], second["maze"]["grid"])
        for left, right in zip(first["algorithms"], second["algorithms"]):
            self.assertEqual(left["algorithm"], right["algorithm"])
            self.assertEqual(left["path"], right["path"])
            self.assertEqual(left["events"], right["events"])
            self.assertEqual(left["metrics"]["nodes_explored"], right["metrics"]["nodes_explored"])
            self.assertEqual(left["metrics"]["frontier_peak"], right["metrics"]["frontier_peak"])
            self.assertEqual(left["metrics"]["path_length"], right["metrics"]["path_length"])
            self.assertEqual(left["metrics"]["path_cost"], right["metrics"]["path_cost"])

    def test_candidate_selection_prefers_divergent_weighted_maze(self) -> None:
        payload = run_algorithm_suite(size=15, seed=11, weighted=True, loop_factor=0.18)
        path_costs = {item["metrics"]["path_cost"] for item in payload["algorithms"]}

        self.assertGreater(len(path_costs), 1)


if __name__ == "__main__":
    unittest.main()
