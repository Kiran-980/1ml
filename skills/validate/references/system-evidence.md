# system evidence

## Diagnostic implementation checks

Select only diagnostics needed for the claim and budget. Reuse saved out-of-fold predictions for development diagnostics rather than silently repeating fits. Selected-candidate CV diagnostics still share selection bias; reserved final evidence has a different role.

- Metric reports: use a single candidate identifier across fitting, selection, serialization and reporting. Generate names and values from the same metric record; assert finite values and label/row alignment. Reconcile promised analyses with those actually executed and label deferred work.
- Calibration tables: derive bin counts, mean predictions and event rates from the same bin assignment. Empty bins may be omitted by a helper, so enumerating its returned values does not recover the original bin indices. Brier score measures overall probability quality, not calibration alone. Logistic regression does not guarantee calibrated probabilities.
- Permutation importance: label results using the columns supplied to the estimator being permuted. A full raw-input pipeline returns raw-column importances; an estimator receiving a transformed matrix returns transformed-column importances. Distinguish training-set description from held-out evidence, and consider correlated or implausible perturbations.
- Artifact checks: make schema, output-domain and reload-parity failures stop completion. Verify serialization in a fresh process with the recorded modules and environment. Synthetic missing/unknown-category checks establish software behavior, not predictive robustness to realistic shifts.

Partition separation protects against particular leakage paths; it does not by itself make related observations statistically independent. Missingness mechanisms require evidence beyond counts. Preserve uncertainty and use actual source locations rather than invented rule identifiers or section numbers.

## 8.1 Validate the frozen system against its intended use

The evaluated object includes data preparation, estimator, calibration, thresholds, retrieval/index where applicable, fallback, and human workflow. Evaluate the locked selection procedure on the reserved test or other appropriately independent design. Record population, time period, exclusions, sample/event counts, baseline, uncertainty, and operational limits. A new threshold or feature chosen after reading the test result needs renewed evaluation.

Use error analysis to decide whether performance is acceptable and to generate future development hypotheses. Inspect expensive mistakes, representative ordinary cases, groups, time periods, and unsupported inputs. Avoid selecting only impressive examples. If a critical use case lacks support, narrow intended use or collect evidence rather than hiding it in a macro average.

Production readiness includes data, model, infrastructure, and monitoring checks. Google's ML Test Score supplies a research rubric; the concrete tests below are 1ml synthesis and must match the actual system rather than be copied mechanically. [ML Test Score](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)

| Failure boundary | Relevant validation | Release consequence |
|---|---|---|
| Schema/semantics | Missing fields, types, units, category changes, invalid ranges | Reject/quarantine or apply a documented fallback |
| Transformation | Serialized-versus-training output parity, row alignment, unknown/missing handling | Repair pipeline before interpreting model metrics |
| Model quality | Baseline comparison, uncertainty, slices, calibration/policy | Release only within supported scope |
| Resource behavior | End-to-end latency percentiles, throughput, peak memory, cold start | Change architecture/model or traffic limits |
| Dependencies | Source outage, stale features, timeout, retry, partial batch | Exercise degraded operation and recovery |
| Reliability | Deterministic invariants, output domain, reproducible replay | Investigate inconsistent predictions or invalid outputs |
| Human process | Review queue, disagreement, escalation, user understanding | Adjust capacity/interface and evaluate combined outcomes |
| Change/rollback | Versioned bundle, canary/shadow evidence, rollback rehearsal | Ensure previous known-good behavior can be restored |


## 8.2 Uncertainty must match the claim

Distinguish a confidence interval for an average metric/parameter, a prediction interval for a new outcome, a calibrated class probability, and uncertainty about model choice or distribution shift. These are not interchangeable. Report intervals with support counts and method assumptions; do not label a score such as 0.9 as '90% confidence' unless that interpretation is justified.

For conformal prediction, select a nonconformity score and calibration scheme appropriate to the task, keep calibration separate as required, and check coverage and interval/set size. Standard guarantees rely on exchangeability and are typically marginal over the calibration/test population; they do not guarantee coverage for every person or arbitrary subgroup. Time dependence/shift needs a justified adapted method rather than reusing the standard guarantee. [Conformal prediction introduction](https://arxiv.org/html/2107.07511v6)

Evaluate coverage and width by relevant slices where sample support permits. An apparently correct average can conceal a poorly covered group. If data are too sparse, say that coverage is unknown. Use abstention or restricted scope only with a measured fallback/review process.


## 8.3 Interpretability and fairness are use-specific analyses

Explain a model only after establishing that it predicts adequately for the question. Held-out permutation importance measures how a fitted model uses features under a perturbation scheme; correlated features can share or mask importance. It does not identify causal effects or universal intrinsic feature value. [Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)

Partial-dependence/ICE plots can probe learned shape, but correlated inputs may make evaluated feature combinations unrealistic. Describe the supported region and avoid treating the curve as the outcome of an intervention. [Partial dependence](https://scikit-learn.org/stable/modules/partial_dependence.html)

Choose fairness analyses from the harm and decision context: selection rates, error rates, calibration, access, quality of service, or other task-specific consequences. Check sample sizes and intersectional groups. Different parity definitions may conflict; one metric passing does not establish fairness of the entire system. Sensitive-feature removal does not eliminate proxy effects. [Fairlearn assessment](https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html)

Document intended and excluded uses, populations, evaluation conditions, ethical considerations, and limitations in a model/system card. This supports review but does not replace stakeholder judgment or required domain review. [Model Cards](https://arxiv.org/abs/1810.03993)


## 8.7 Release decision

The release record connects offline results, relevant experiment evidence, operating constraints, known unsupported cases, monitoring ownership, and rollback readiness. Some projects stop at a notebook, descriptive report, data acquisition plan, or human-reviewed pilot. Those are legitimate endpoints; production release is conditional on intended use and evidence, not an obligatory final stage of every analysis.

### Resolve a failed or inconclusive gate

| Result | Route and decision |
|---|---|
| Pipeline/data contract fails | Repair the failing boundary and rerun affected checks; the quality score does not override an invalid input/output contract. |
| Quality misses the required practical improvement | Diagnose using development evidence; keep the baseline, improve data/model, or revise the use case with the owner. Avoid repeated test-driven optimization. |
| Point estimate improves but uncertainty is too wide | Report inconclusive evidence; collect a better evaluation sample or reduce the claim. A pilot needs its own bounded objective and exposure policy. |
| Average passes but a critical slice fails | Address coverage/model/policy or narrow intended use with explicit constraints; aggregate success does not automatically authorize the failing use. |
| Predictive quality passes but latency/cost/review capacity fails | Change the model/system/policy and repeat affected end-to-end evaluation. Threshold changes can alter quality and workload together. |
| Offline metric passes but intervention value fails | Check experiment integrity and proxy alignment. If the effect is genuinely unfavorable, keep the incumbent or reframe rather than promoting on offline performance. |
| Experiment has assignment/logging failure | Diagnose and establish a trustworthy analysis/re-run; more sample size does not fix a biased experiment. |
| Candidate meets a prespecified acceptable-equivalence margin while reducing costs | Consider replacement if all guardrails pass and the business tradeoff is accepted; superiority on every metric is unnecessary. |

If development resumes after final-test inspection, retain the original results as history and follow [evaluation invalidation](../../evaluation/references/labels-splits.md#35-gate-and-invalidation). The exact fitted/calibrated/policy bundle reaching release must match the [final fitting protocol](../../train/references/final-fitting.md#610-refitting-calibration-and-policy-order).

Robustness checks should reflect plausible deployment changes: source missingness, measurement error, delayed fields, changed devices, or relevant subpopulations. Prespecify domain-valid invariances when available; arbitrary feature perturbations can create impossible examples and do not establish meaningful robustness. If the system abstains, evaluate the fallback's quality, capacity, and response time as well as accepted predictions.
