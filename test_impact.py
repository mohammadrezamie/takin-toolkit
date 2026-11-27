import unittest
from impact import select_feedback

class ImpactTests(unittest.TestCase):
    expected = ["unit", "integration", "security", "unrelated"]
    graph = {"core": [], "service": ["core"], "ui": ["service"], "other": [], "auth": []}
    targets = {"unit": ["core"], "integration": ["ui"], "security": ["auth"], "unrelated": ["other"]}

    def run_selection(self, changed, **overrides):
        return select_feedback(self.expected, overrides.pop("dependencies", self.graph),
                               overrides.pop("test_targets", self.targets), changed, **overrides)

    def test_transitive_and_critical(self):
        result = self.run_selection(["core"], mandatory=["security"])
        self.assertEqual(result["selected"], ["integration", "security", "unit"])
        self.assertEqual(result["omitted_for_feedback"], ["unrelated"])
        self.assertEqual(result["mode"], "targeted")

    def test_direction_of_edges(self):
        result = self.run_selection(["ui"])
        self.assertEqual(result["selected"], ["integration"])

    def test_global_and_unknown_full(self):
        for result in (self.run_selection(["core"], global_change=True),
                       self.run_selection(["unknown"]), self.run_selection([]),
                       self.run_selection(["core"], dependencies=None)):
            self.assertEqual(result["mode"], "full")
            self.assertEqual(result["selected"], sorted(self.expected))
            self.assertEqual(result["omitted_for_feedback"], [])

    def test_incomplete_graph_full(self):
        for result in (
            self.run_selection(["core"], dependencies=dict(self.graph, ui=["missing"])),
            self.run_selection(["core"], test_targets={"unit": ["core"]}),
            self.run_selection(["core"], test_targets=dict(self.targets, integration=[])),
            self.run_selection(["core", "orphan"], dependencies=dict(self.graph, orphan=[])),
        ):
            self.assertEqual(result["mode"], "full")
            self.assertEqual(result["selected"], sorted(self.expected))

    def test_cycle_and_generators(self):
        graph = dict(self.graph, core=iter(["ui"]), ui=iter(["service"]), service=iter(["core"]))
        result = self.run_selection(["core"], dependencies=graph)
        self.assertEqual(result["selected"], ["integration", "unit"])

    def test_invalid_input(self):
        for changed, opts in ((["core", "core"], {}), ("core", {}), (["core"], {"mandatory": ["missing"]}),
                              (["core"], {"global_change": 1})):
            with self.subTest(changed=changed, opts=opts), self.assertRaises(ValueError):
                self.run_selection(changed, **opts)
