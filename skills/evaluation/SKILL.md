---
name: evaluation
description: Define or review labels, metrics, split design, leakage boundaries, and validation roles for a specified claim. Use before predictive selection or when outcomes, costs, population, timing, or independence assumptions change.
---

# Define what the evidence must establish

Resolve Markdown links relative to this skill's directory, preserving `../` segments. The shared `../../references/tasks/index.md` is `<plugin-root>/references/tasks/index.md`, not a file under this skill's `references/`. Read the linked path; do not invent filenames or search the whole filesystem after a failed read.

Start from the intended claim and current data semantics, using [state](../../references/project-state.md) for existing work. If the action is unclear, return the precise missing question to [frame](../frame/SKILL.md); if timestamps, keys, or outcome availability are unknown, use [data](../data/SKILL.md). Do not reopen unrelated completed stages.

For an explanation or design review without project artifacts, use the methodological references only. State and notebook protocols below apply when inspecting, creating, or updating project records; do not load them just to answer the question.

## Choose relevant references

| Condition | Read before deciding |
|---|---|
| Prediction unit/output, horizon, or objective unclear | [Task contract](references/task-contract.md) |
| Metric, loss, averaging, costs/capacity, calibration, ordered/partial targets | [Metrics and policy](references/metrics-policy.md) |
| Labels, maturity, groups, time, source overlap, or final holdout | [Labels and splits](references/labels-splits.md) |
| Too few groups/events, incompatible split requirements, or internal CV | [Feasibility and inner validation](references/inner-validation.md) |
| Forecasting, censored outcomes, causal effect, ranking or other specialist claim | Matching [task profile](../../references/tasks/index.md) immediately |

## Establish the design

Define observation/decision time, target construction, maturation and unknown/censored outcomes. Choose the population and what “unseen” means: new records, entities, future periods, sites, or combinations. Prevent related observations and future information from crossing the relevant boundary.

Choose the business outcome, learning loss, selection metric, and decision policy separately. Record denominators, weighting/aggregation, practical thresholds, uncertainty, critical slices, and operational guardrails. Undefined scores remain visible; do not silently discard folds or failing predictions. Imbalance alone does not determine the metric.

Assign development, selection, calibration/policy, and final evaluation roles only where needed. Record splitter parameters, IDs/manifests, seeds, time cutoffs, gaps, and label eligibility. Every learned transform and internal validation procedure must respect those roles. A framework's default cross-validation may violate grouped or temporal requirements.

Inspect feasibility before fitting: class/event support and independent units must support the requested claim. If no valid split exists, acquire evidence, simplify fitted choices, narrow the claim with the owner, or report uncertainty; randomizing away a required group/time boundary is not a repair. Descriptive inference may use the observed sample under its sampling design, without a compulsory prediction holdout.

## Completion and connections

Persist the metric/policy contract, label definition, split evidence, eligibility rules, and explicit limitations using the [notebook protocol](../../references/notebook-protocol.md). Complete only when the requested design is justified or its infeasibility is explained. Record the appropriate outcome separately from execution status.

Send valid design to [explore](../explore/SKILL.md), [prepare](../prepare/SKILL.md), or [train](../train/SKILL.md) as the request requires. Final fitting/calibration questions use [train's final-fitting protocol](../train/references/final-fitting.md). Intervention effects use [experiment](../experiment/SKILL.md). Any change to labels, split, or metric invalidates the affected downstream artifacts; inspecting a final test and then adapting requires renewed evaluation, not reuse of its untouched-test label.
