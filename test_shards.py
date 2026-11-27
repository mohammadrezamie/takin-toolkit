import unittest
from shards import partition

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
