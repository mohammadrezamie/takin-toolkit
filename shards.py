"""Deterministic, balanced partitioning of independent work items."""
from collections.abc import Mapping
import heapq


def partition(items, count):
    if type(count) is not int or count < 1:
        raise ValueError("count must be a positive integer")
    items = list(items)
    if any(not isinstance(item, str) or not item for item in items):
        raise ValueError("item IDs must be non-empty strings")
    if len(set(items)) != len(items):
        raise ValueError("duplicate item ID")
    groups = [[] for _ in range(count)]
    for index, item in enumerate(sorted(items)):
        groups[index % count].append(item)
    return groups


def partition_by_duration(items, count, durations_ms=None, *, default_ms=1000):
    """Longest-processing-time-first estimate for independent work.

    Timings are positive integer milliseconds; unknown items receive default_ms.
    Reject stale IDs rather than silently mixing unrelated timing manifests.
    This predicts load, not actual wall time or safe concurrency.
    """
    items = list(items)
    groups = partition(items, count)
    if type(default_ms) is not int or default_ms < 1:
        raise ValueError("default duration must be a positive integer")
    if durations_ms is None:
        durations_ms = {}
    if not isinstance(durations_ms, Mapping):
        raise ValueError("durations must be a mapping")
    known = set(items)
    if any(key not in known for key in durations_ms):
        raise ValueError("unknown timing item")
    if any(type(value) is not int or value < 1 for value in durations_ms.values()):
        raise ValueError("durations must be positive integers")

    groups = [[] for _ in groups]
    loads = [0] * count
    available = [(0, 0, index) for index in range(count)]
    heapq.heapify(available)
    ordered = sorted(items, key=lambda item: (-durations_ms.get(item, default_ms), item))
    for item in ordered:
        load, size, index = heapq.heappop(available)
        groups[index].append(item)
        loads[index] = load + durations_ms.get(item, default_ms)
        heapq.heappush(available, (loads[index], size + 1, index))
    return groups, loads
