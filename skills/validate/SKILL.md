---
name: validate
description: Evaluate a frozen model and decision system against intended-use evidence and guardrails. Use for independent quality, uncertainty, slice, interpretation, fairness, robustness, or readiness checks; model selection belongs to train.
---

# Validate the exact decision system

For a design-only review, load system evidence but not project-state or notebook files. Resolve links relative to this skill directory, preserving `../`; shared files live under the plugin root's `references/`.

Identify the frozen preprocessing, estimator, calibration, policy, fallback, and human workflow. Confirm data lineage, independent evaluation role, supported population, metrics, costs, and thresholds. Read [system evidence and release decisions](references/system-evidence.md) and relevant [state](../../references/project-state.md). Use the selected [task profile](../../references/tasks/index.md) when evaluation semantics differ.

Measure the whole system under its declared use, not only successful predictions. Report sample/event support, uncertainty, slices, exclusions, failures, review/fallback workload, and operational limits. Distinguish calibrated probabilities, metric confidence intervals, prediction intervals, and distribution-shift uncertainty. Conformal guarantees require their stated calibration/exchangeability conditions; average coverage does not guarantee every subgroup.

For a fixed set of scores and evaluation population, changing the action threshold changes workload, precision/recall and costs, not the score-ranking AUROC. Re-evaluate the affected policy outcomes. Excluding failed/abstained cases can bias quality in either direction; report selective score metrics with coverage and full-workflow outcomes rather than asserting every omitted-case score must be inflated.

Choose explanation and fairness analyses for the actual claim and harm context. Permutation importance and partial dependence describe model behavior under assumptions, not causal effects. Correlated inputs can distort perturbations. Passing one parity metric does not establish fairness of the system.

Check schema, units, unknown/missing handling, row alignment, packaged parity, dependencies, latency/memory, fallback behavior, and rollback readiness to the extent relevant. Use domain-valid perturbations; impossible feature combinations do not demonstrate useful robustness. Keep final-test inspection separate from adaptive development: changes based on its result require renewed evaluation and invalidation.

Required artifact checks must assert or raise on failure; printing `FAILED` or catching an exception without failing does not pass a gate. Reuse saved evaluation predictions within their declared role, and make summaries name the actual population, candidate and metric. Read [diagnostic implementation checks](references/system-evidence.md#diagnostic-implementation-checks) only when implementing those diagnostics. Separate observed results, untested plans, and assumptions; neither a sealed split nor a model family guarantees independence or calibration.

When a notebook is a requested deliverable, apply the [notebook completion review](../../references/notebook-protocol.md#review-before-calling-the-notebook-complete) to the actual saved analysis and figures. Check that its decisions and transitions are explained and agree with measured evidence, separately from execution and model-parity checks. Repair presentation gaps without changing a frozen candidate in response to final-test outcomes; disclose any remaining verification gap.

For an end-to-end request, reconcile the lifecycle coverage record with executed evidence, including preparation checks and development error diagnostics. A high aggregate score, a figure count, or a fresh-process reload pass cannot stand in for these analyses. Return missing applicable computations to the owning skill before final-test inspection; after final-test inspection, retain the frozen bundle and distinguish added diagnostics from model adaptation requiring renewed evaluation.

## Decide and route

- Contract/pipeline failure: return the failing evidence to [data](../data/SKILL.md) or [prepare](../prepare/SKILL.md).
- Quality/support failure: return a development hypothesis to [train](../train/SKILL.md), or a population/collection limitation to [frame](../frame/SKILL.md); preserve test history.
- Inconclusive precision: state what evidence is missing; keep the baseline or define a bounded learning pilot.
- Critical slice or workload failure: repair the policy/system or narrow supported use with the owner. Average quality does not override it.
- Predictive success with an unresolved intervention claim: use [experiment](../experiment/SKILL.md).
- Supported requested operational use: pass the exact bundle and release record to [release](../release/SKILL.md).

Save actual results, intended/excluded uses, limits, and the decision in the [notebook](../../references/notebook-protocol.md). An analysis report can be the endpoint. Equivalent quality with an accepted cost benefit can justify replacement; superiority on every metric is not mandatory. A score alone does not authorize deployment.
