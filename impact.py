"""Conservative dependency-based selection for fast development feedback.

Never a substitute for the complete release manifest. No filesystem or network.
"""
from collections.abc import Mapping

def _ids(values, label):
    if isinstance(values, (str, bytes, Mapping)):
        raise ValueError(f"{label} must be a collection of identifiers")
    values = list(values)
    if any(not isinstance(x, str) or not x.strip() or x != x.strip() for x in values):
        raise ValueError(f"invalid {label} identifier")
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate {label} identifier")
    return set(values)

def select_feedback(expected, dependencies, test_targets, changed, *, mandatory=(), global_change=False):
    """Return selected case IDs and reasons; dependency edges point to prerequisites.

    A -> B means A depends on B; changes to B affect A transitively.
    Missing or unknown graph coverage and explicitly global changes select all.
    Callers must construct an accurate graph and independently classify global inputs.
    """
    expected = _ids(expected, "expected")
    if not expected:
        raise ValueError("empty test manifest")
    changed = _ids(changed, "changed")
    mandatory = _ids(mandatory, "mandatory")
    if not mandatory <= expected:
        raise ValueError("unknown mandatory case")
    if type(global_change) is not bool:
        raise ValueError("global_change must be boolean")

    def full(reason):
        return {"selected": sorted(expected), "omitted_for_feedback": [],
                "mode": "full", "reason": reason}

    if global_change:
        return full("global change")
    if not isinstance(dependencies, Mapping) or not isinstance(test_targets, Mapping):
        return full("missing dependency graph")
    modules = _ids(dependencies.keys(), "module")
    targets = _ids(test_targets.keys(), "mapped case")
    if targets != expected:
        return full("incomplete test mapping")
    reverse = {module: set() for module in modules}
    graph = {module: _ids(prerequisites, "prerequisite") for module, prerequisites in dependencies.items()}
    for module, prerequisites in graph.items():
        for prerequisite in prerequisites:
            if prerequisite not in modules:
                return full("unknown dependency")
            reverse[prerequisite].add(module)
    owners = {module: set() for module in modules}
    for test, raw in test_targets.items():
        mapped = _ids(raw, "test target")
        if not mapped or not mapped <= modules:
            return full("unmapped test target")
        for module in mapped:
            owners[module].add(test)
    if not changed:
        return full("empty change set")
    if not changed <= modules:
        return full("unknown changed module")
    affected = set(changed)
    pending = list(changed)
    while pending:
        for dependent in reverse[pending.pop()]:
            if dependent not in affected:
                affected.add(dependent)
                pending.append(dependent)
    # Check every changed module reaches at least one test, even in a mixed diff.
    # Compute the set of modules that can reach a tested dependent, including cycles.
    covered = {module for module in modules if owners[module]}
    pending = list(covered)
    while pending:
        for prerequisite in graph[pending.pop()]:
            if prerequisite not in covered:
                covered.add(prerequisite)
                pending.append(prerequisite)
    if not changed <= covered:
        return full("changed module lacks mapped coverage")
    selected = mandatory | set().union(*(owners[module] for module in affected))
    if not selected:
        return full("no mapped feedback cases")
    return {"selected": sorted(selected), "omitted_for_feedback": sorted(expected - selected),
            "mode": "full" if selected == expected else "targeted",
            "reason": "transitive impact and mandatory cases"}
