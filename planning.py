"""Bounded planning for independent work; estimates are not billed usage."""
from shards import partition_by_duration

def _integer(value, minimum, name):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")

def choose_plan(items, durations_ms=None, *, max_workers, budget_ms, setup_ms=0,
                quantum_ms=1, default_ms=1000):
    """Choose fastest estimated feasible plan, then least compute, then workers.

    Every nonempty shard incurs setup and rounds compute up to quantum_ms.
    Budget includes all shards. Caller sets an independently justified worker
    ceiling and uses only isolated work. No execution or provider dispatch.
    """
    _integer(max_workers, 1, "max_workers")
    _integer(budget_ms, 0, "budget_ms")
    _integer(setup_ms, 0, "setup_ms")
    _integer(quantum_ms, 1, "quantum_ms")
    items = list(items)
    if not items:
        # Still validate timing and default inputs.
        partition_by_duration(items, 1, durations_ms, default_ms=default_ms)
        raise ValueError("nonempty independent manifest required")
    options = []
    for workers in range(1, min(max_workers, len(items)) + 1):
        groups, loads = partition_by_duration(items, workers, durations_ms, default_ms=default_ms)
        elapsed = [load + setup_ms for load in loads]
        compute = sum(((value + quantum_ms - 1) // quantum_ms) * quantum_ms for value in elapsed)
        options.append({"workers": workers, "groups": groups, "loads_ms": loads,
                        "wall_ms": max(elapsed), "compute_ms": compute,
                        "feasible": compute <= budget_ms})
    feasible = [option for option in options if option["feasible"]]
    best = min(feasible, key=lambda x: (x["wall_ms"], x["compute_ms"], x["workers"])) if feasible else None
    return {"selected": best, "options": options}
