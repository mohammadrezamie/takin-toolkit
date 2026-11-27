import unittest
from shards import partition, partition_by_duration

class PartitionTests(unittest.TestCase):
    def test_exact_coverage(self):
        items = [str(i) for i in range(103)]
        groups = partition(items, 10)
        self.assertEqual(sorted(sum(groups, [])), sorted(items))
        self.assertLessEqual(max(map(len, groups)) - min(map(len, groups)), 1)
    def test_deterministic(self):
        self.assertEqual(partition(["b", "a", "c"], 2), partition(["c", "b", "a"], 2))
    def test_empty_groups(self):
        self.assertEqual(partition([], 3), [[], [], []])
        self.assertEqual(partition(["a"], 3), [["a"], [], []])
    def test_invalid(self):
        for items, count in [(["a", "a"], 2), ([""], 2), ([1], 2), ([], 0), ([], True)]:
            with self.subTest(items=items, count=count), self.assertRaises(ValueError):
                partition(items, count)


class DurationPartitionTests(unittest.TestCase):
    def test_skewed_fixture(self):
        items = ["a", "b", "c", "d"]
        durations = {"a": 100, "b": 1, "c": 100, "d": 1}
        baseline = max(sum(durations[i] for i in g) for g in partition(items, 2))
        groups, loads = partition_by_duration(items, 2, durations)
        self.assertEqual(baseline, 200)
        self.assertEqual(loads, [101, 101])
        self.assertEqual(sorted(sum(groups, [])), items)

    def test_deterministic_and_exact_once(self):
        items = [str(i) for i in range(103)]
        durations = {i: (int(i) + 1) ** 2 for i in items}
        groups, loads = partition_by_duration(items, 10, durations)
        self.assertEqual((groups, loads), partition_by_duration(reversed(items), 10, dict(reversed(list(durations.items())))))
        self.assertEqual(sorted(sum(groups, [])), sorted(items))
        self.assertEqual(sum(loads), sum(durations.values()))
        self.assertEqual(loads, [sum(durations[i] for i in g) for g in groups])

    def test_unknown_duration_and_empty_groups(self):
        self.assertEqual(partition_by_duration(["a", "b"], 3, {"a": 2000}, default_ms=250),
                         ([["a"], ["b"], []], [2000, 250, 0]))
        self.assertEqual(partition_by_duration([], 2), ([[], []], [0, 0]))

    def test_reject_bad_inputs(self):
        for durations in ({"b": 1}, {"a": 0}, {"a": True}, {"a": -1}, {"a": 1.5}, {"a": float("inf")}, []):
            with self.subTest(durations=durations), self.assertRaises(ValueError):
                partition_by_duration(["a"], 2, durations)
        for default in (0, True, -1, 1.5):
            with self.subTest(default=default), self.assertRaises(ValueError):
                partition_by_duration(["a"], 2, default_ms=default)
        for items, count in ((["a", "a"], 2), ([""], 2), (["a"], 0)):
            with self.subTest(items=items, count=count), self.assertRaises(ValueError):
                partition_by_duration(items, count)
