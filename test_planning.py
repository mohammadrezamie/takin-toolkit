import unittest
from planning import choose_plan

class BudgetPlanTests(unittest.TestCase):
    def test_budget_constrains_parallelism(self):
        items = ["a", "b", "c", "d"]
        durations = dict.fromkeys(items, 100)
        result = choose_plan(items, durations, max_workers=4, budget_ms=500, setup_ms=50)
        self.assertEqual(result["selected"]["workers"], 2)
        self.assertEqual(result["selected"]["wall_ms"], 250)
        self.assertEqual(result["selected"]["compute_ms"], 500)
        self.assertFalse(result["options"][2]["feasible"])

    def test_fastest_under_larger_budget(self):
        result = choose_plan(["a", "b", "c", "d"], max_workers=10, budget_ms=6000, setup_ms=100)
        self.assertEqual(result["selected"]["workers"], 4)
        self.assertEqual(len(result["options"]), 4)
        self.assertEqual(result["selected"]["wall_ms"], 1100)

    def test_rounding_can_rule_out_extra_workers(self):
        result = choose_plan(["a", "b"], {"a": 31, "b": 29}, max_workers=2,
                             budget_ms=60, quantum_ms=60)
        self.assertEqual(result["selected"]["workers"], 1)
        self.assertEqual(result["options"][1]["compute_ms"], 120)

    def test_no_feasible_plan_is_explicit(self):
        result = choose_plan(["a"], max_workers=8, budget_ms=0)
        self.assertIsNone(result["selected"])
        self.assertEqual(len(result["options"]), 1)

    def test_deterministic_coverage_and_tie(self):
        items = ["b", "a", "c"]
        durations = {"a": 1000, "b": 1, "c": 1}
        kwargs = dict(max_workers=3, budget_ms=10000, setup_ms=50)
        result = choose_plan(items, durations, **kwargs)
        self.assertEqual(result, choose_plan(reversed(items), durations, **kwargs))
        self.assertEqual(result["selected"]["workers"], 2)
        for option in result["options"]:
            self.assertEqual(sorted(sum(option["groups"], [])), sorted(items))
            self.assertEqual(sum(option["loads_ms"]), 1002)

    def test_invalid_inputs(self):
        for kwargs in ({"max_workers": 0}, {"max_workers": True}, {"budget_ms": -1},
                       {"setup_ms": -1}, {"quantum_ms": 0}, {"default_ms": False}):
            args = {"max_workers": 2, "budget_ms": 5000, **kwargs}
            with self.subTest(args=args), self.assertRaises(ValueError):
                choose_plan(["a"], **args)
        for items in ([], ["a", "a"], [""]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                choose_plan(items, max_workers=2, budget_ms=5000)
