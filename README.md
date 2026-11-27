# takin-toolkit

Deterministic, dependency-free utilities for planning independent work and conservative development feedback.

## Run locally

\`\`\`sh
python3 -m unittest discover -v
\`\`\`

Uses standard-library dependencies only. CI runs this repository's own code and synthetic tests on two standard Linux runner images in parallel. Failed jobs remain visible; no private checkout, cross-repository tokens, deployment, production data or private test artifacts are used.

## Partitioning and budget-aware planning

- \`partition(items, count)\` balances item counts deterministically.
- \`partition_by_duration(items, count, durations_ms, default_ms=1000)\` uses a longest-processing-time-first heuristic for independent tasks.
- \`planning.choose_plan(...)\` chooses the fastest estimated plan within an explicit compute budget and worker ceiling.

These are estimates, not billed usage or guarantees of throughput. The caller owns resource isolation and safe worker ceilings.

## Dependency and exclusive-resource scheduling

\`schedule.schedule_waves(items, max_workers=..., dependencies=..., resources=...)\` creates deterministic waves. A task starts only after its prerequisites have completed in earlier waves; tasks sharing an exclusive resource label never occupy the same wave. Unknown dependencies, incomplete maps, cycles and invalid inputs fail closed. This is a plan only: it does not execute tasks, provide distributed locks or prove that a resource label captures every real-world conflict.

## Conservative feedback selection

\`impact.select_feedback(expected, dependencies, test_targets, changed, mandatory=(), global_change=False)\` walks reverse dependency edges to identify transitively affected cases and always includes designated mandatory cases. Unknown changes, incomplete mappings, uncovered modules, empty changes and global inputs select the full suite. The caller must build an accurate graph; this is development feedback only, not a release waiver. No private dependency graph, test names or change metadata is sent to public CI.

## Integration boundary

This is an independently useful public utility, not a mirror or remote runner for a private application. Consumers should pin a reviewed version and run their own integration checks. A green public CI run certifies only this utility at its tested commit, not any consuming application.

## Status

Initial implementation; not a stable release. Licensing terms are pending owner selection; public visibility alone is not a license to redistribute or modify.
