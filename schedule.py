"""Deterministic scheduling waves with prerequisites and exclusive resources.

This plans work only; it does not execute jobs or guarantee runtime isolation.
"""
from collections.abc import Mapping


def _ids(values, label):
    if isinstance(values, (str, bytes, Mapping)):
        raise ValueError(f"{label} must be a collection of identifiers")
    try:
        values = list(values)
    except TypeError as exc:
        raise ValueError(f"{label} must be iterable") from exc
    if any(not isinstance(value, str) or not value or value != value.strip() for value in values):
        raise ValueError(f"invalid {label} identifier")
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate {label} identifier")
    return set(values)


def _mapping(items, value, label):
    if value is None:
        return {item: set() for item in items}
    if not isinstance(value, Mapping) or set(value) != items:
        raise ValueError(f"{label} must map every task exactly once")
    return {item: _ids(value[item], label) for item in items}


def schedule_waves(items, *, max_workers, dependencies=None, resources=None):
    """Return deterministic ready-to-run waves.

    A task is eligible only after all prerequisites complete in earlier waves.
    Tasks in one wave may not share an exclusive resource ID. Tasks without
    resources may share a wave with any other eligible task. When multiple
    tasks are ready, lexical task order wins. Cycles and unknown references
    raise ValueError. Empty input returns no waves.

    This is a conservative planning primitive, not a process runner, lock
    manager, database isolation check or proof that the supplied graph is
    complete. Resource IDs are caller-defined exclusive labels.
    """
    if type(max_workers) is not int or max_workers < 1:
        raise ValueError("max_workers must be a positive integer")
    task_ids = _ids(items, "task")
    prerequisites = _mapping(task_ids, dependencies, "dependencies")
    locks = _mapping(task_ids, resources, "resources")
    for task, required in prerequisites.items():
        if not required <= task_ids:
            raise ValueError(f"unknown prerequisite for {task}")

    completed = set()
    waves = []
    while completed != task_ids:
        ready = sorted(task for task in task_ids - completed
                       if prerequisites[task] <= completed)
        if not ready:
            raise ValueError("dependency cycle")
        wave = []
        reserved = set()
        for task in ready:
            if len(wave) >= max_workers:
                break
            if locks[task].isdisjoint(reserved):
                wave.append(task)
                reserved.update(locks[task])
        if not wave:
            raise ValueError("no schedulable task")
        waves.append(wave)
        completed.update(wave)

    return {"waves": waves, "order": [task for wave in waves for task in wave],
            "wave_count": len(waves), "task_count": len(task_ids)}
