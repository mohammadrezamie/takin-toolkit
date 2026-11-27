# takin-toolkit

Deterministic work partitioning: sorted unique item IDs are distributed across N shards with group sizes differing by at most one. This balances item counts, not measured runtimes. For heterogeneous independent work, `partition_by_duration(items, count, durations_ms, default_ms=1000)` places the longest estimated items first into the least-loaded shard and returns groups plus estimated total milliseconds. Timing IDs must match the manifest; unknown durations use an explicit positive default. This is a scheduling heuristic, not a concurrency safety check or a measured speedup.

Synthetic example: four items with estimated durations 100, 1, 100, 1 ms yield a 200 ms maximum group load with count-based partitioning and 101 ms with duration-aware allocation. Actual setup, CPU, I/O and queue times must be benchmarked separately. Private workload manifests and timings stay in their private execution environment.

## Run locally

```sh
python3 -m unittest discover -v
```

Uses standard-library dependencies only. CI runs this repository's own code and synthetic tests on two standard Linux runner images in parallel. Failed jobs remain visible; no private checkout, cross-repository tokens, deployment, production data or private test artifacts are used.

## Budget-aware worker selection

`planning.choose_plan(items, durations_ms, max_workers=..., budget_ms=..., setup_ms=..., quantum_ms=...)` compares deterministic duration-balanced plans from one worker through the caller's safe ceiling. It chooses the smallest estimated critical path within the total compute budget, breaking ties by compute and worker count. It accounts for repeated setup and configurable rounding; no feasible plan returns an explicit null selection, never an incomplete suite. Example: four 100 ms items, 50 ms setup per worker and 500 ms compute budget selects two workers (250 ms wall, 500 ms compute) rather than four (150 ms wall, 600 ms compute). These are synthetic estimates, not actual billed minutes or throughput. Queue time, contention, provider pricing and isolation require separate measurement. No execution or dispatch is performed by the planner.

## Integration boundary

This is an independently useful public utility, not a mirror or remote runner for a private application. Consumers should pin a reviewed version and run their own integration checks. A green public CI run certifies only this utility at its tested commit, not any consuming application.

## Status

Initial implementation; not a stable release. Licensing terms are pending owner selection; public visibility alone is not a license to redistribute or modify.
