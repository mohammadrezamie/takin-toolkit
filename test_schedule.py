import unittest
from schedule import schedule_waves


class ScheduleTests(unittest.TestCase):
    def test_exact_coverage_and_worker_limit(self):
        tasks = [f"task-{i:02d}" for i in range(23)]
        result = schedule_waves(tasks, max_workers=4)
        self.assertEqual(sorted(result["order"]), sorted(tasks))
        self.assertEqual(len(result["order"]), len(set(result["order"])))
        self.assertTrue(all(1 <= len(wave) <= 4 for wave in result["waves"]))

    def test_prerequisites_run_in_earlier_waves(self):
        result = schedule_waves(["app", "db", "unit", "api"], max_workers=4,
                                dependencies={"app": ["api"], "db": [], "unit": ["db"], "api": ["db"]})
        positions = {task: index for index, wave in enumerate(result["waves"]) for task in wave}
        self.assertLess(positions["db"], positions["api"])
        self.assertLess(positions["db"], positions["unit"])
        self.assertLess(positions["api"], positions["app"])

    def test_exclusive_resources_never_share_a_wave(self):
        result = schedule_waves(["a", "b", "c", "d"], max_workers=4,
                                resources={"a": ["database"], "b": ["database"],
                                           "c": ["browser"], "d": []})
        self.assertEqual(result["waves"][0], ["a", "c", "d"])
        self.assertEqual(result["waves"][1], ["b"])

    def test_resource_constraints_and_dependencies_compose(self):
        result = schedule_waves(["a", "b", "c"], max_workers=3,
                                dependencies={"a": [], "b": [], "c": ["a"]},
                                resources={"a": ["db"], "b": ["db"], "c": []})
        self.assertEqual(result["waves"], [["a"], ["b", "c"]])

    def test_deterministic_regardless_of_input_order(self):
        kwargs = {"max_workers": 3,
                  "dependencies": {"a": [], "b": [], "c": ["a"], "d": ["b"]},
                  "resources": {"a": ["db"], "b": ["browser"], "c": [], "d": []}}
        self.assertEqual(schedule_waves(["a", "b", "c", "d"], **kwargs),
                         schedule_waves(["d", "c", "b", "a"], **kwargs))

    def test_cycles_and_unknown_dependencies_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            schedule_waves(["a", "b"], max_workers=2, dependencies={"a": ["b"], "b": ["a"]})
        with self.assertRaisesRegex(ValueError, "unknown prerequisite"):
            schedule_waves(["a"], max_workers=1, dependencies={"a": ["missing"]})

    def test_incomplete_maps_and_invalid_resources_fail(self):
        with self.assertRaisesRegex(ValueError, "every task"):
            schedule_waves(["a", "b"], max_workers=1, resources={"a": []})
        with self.assertRaises(ValueError):
            schedule_waves(["a"], max_workers=1, resources={"a": ["db", "db"]})
        for workers in (0, True, -1, 1.5):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                schedule_waves(["a"], max_workers=workers)

    def test_empty_input(self):
        self.assertEqual(schedule_waves([], max_workers=2),
                         {"waves": [], "order": [], "wave_count": 0, "task_count": 0})


if __name__ == "__main__":
    unittest.main()
