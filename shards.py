"""Deterministic, balanced partitioning of independent work items."""
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
