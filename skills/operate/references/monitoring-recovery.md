# monitoring recovery

## 9.4 Monitor different failure classes separately

| Signal class | Examples | Interpretation and next action |
|---|---|---|
| Service health | Errors, latency percentiles, timeout, queue length, cost | Reliability failure; inspect deployment/dependencies/load first |
| Data integrity | Missing columns, invalid types/ranges, duplicated events, stale features | Contract or collection failure; repair/quarantine/fallback |
| Training-serving skew | Different transformations, units, code, source definitions | Reproduce exact request and compare pipeline stages |
| Covariate/input drift | Changed input distributions or category frequencies | Population/process may have changed; assess relevance and impact |
| Prediction drift | Changed score/class/rank distribution | Could reflect inputs, model/policy version, or bug; investigate |
| Outcome prevalence shift | Changed observed event rate in a comparable mature cohort | Check sampling, label process, policy, and calibration |
| Concept/relationship change | Changed relationship between inputs and outcomes | Requires outcome evidence or assumptions; univariate drift alone cannot establish it |
| Predictive performance | Mature-label metric, calibration, coverage, slice failures | Compare comparable windows and uncertainty; diagnose before retraining |
| Business/human outcomes | Value, harms, complaints, review burden, intervention effects | Revisit policy and framing, even if offline metric remains stable |

Schema/stats validation can detect anomalies, skew, and drift; it does not alone measure business value or prove a concept change. [TensorFlow Data Validation](https://www.tensorflow.org/tfx/data_validation/get_started)

Define each monitor's baseline, population, window, minimum support, effect-size criterion, alert threshold, expected seasonal behavior, and owner. A statistically significant drift test on a huge sample may be operationally trivial; a small rare slice can be important despite weak statistical power. Many simultaneous monitors create alert noise; use an agreed triage policy. No single PSI/KS threshold is universal.


## 9.5 Delayed labels and policy feedback

Join predictions to outcomes using stable IDs, prediction time, horizon, and label version. Report label completeness and maturation. Compare like-for-like cohorts; recent incomplete negatives can falsely suggest improvement. Track unreviewed/unlabeled cases separately from verified negatives.

When a model controls who receives an action or label, future training data reflect that policy. Examples include fraud review, recommendation exposure, and credit approval. Preserve assignment/exposure/action logs and assess whether representative labels or randomized exploration are feasible and appropriate. Simple retraining on observed positives can amplify blind spots. Return to [causal/feedback routes](../../../references/tasks/index.md) when selection affects the claim.


## 9.6 Retraining is a candidate response, not an automatic cure

For an alert: validate the signal; check data/contracts and deployment changes; separate measurement failure from population or relationship change; estimate consequence; choose rollback, source repair, recalibration, policy adjustment, new data, retraining, or reduced scope. Broken features should be repaired before training another model on them.

Scheduled retraining can be appropriate when a validated cadence matches the process; trigger-based retraining can be appropriate when drift/performance evidence warrants it. Both require candidate evaluation, reproducible data, and release gates. A replacement must meet the prespecified improvement or acceptable-equivalence criteria and current guardrails. Equivalent quality with lower cost or restored compatibility can justify a replacement if that tradeoff was explicitly accepted; novelty alone cannot.

Use a sufficiently current evaluation window without forgetting rare events, seasonal conditions, and prior incidents. Keep a meaningful champion comparison and track revisions to labels/feature definitions. Revisit model choice if the data regime or operating requirements change.

### Refresh data without silently changing the experiment

Version incoming extracts, revised labels, feature definitions, and collection-policy changes. Assign new related entities/events consistently with the declared evaluation design; do not re-randomize an accumulating dataset so yesterday's test records become today's training records unnoticed. A deliberately advancing temporal evaluation window is valid when its rules are defined and lineage is retained. Compare incumbent and candidate on comparable current cohorts, and retain incident/rare-case checks where still relevant.

Streaming inference does not imply online training. If the model is explicitly updated incrementally, assess predictions before learning from the corresponding outcomes and honor outcome delay; maintain replayable model/update lineage and a recovery policy. A stream evaluation can be prequential rather than a single fixed holdout, but its chronological and feedback assumptions must be stated. [River progressive evaluation](https://riverml.xyz/latest/api/evaluate/progressive-val-score/)


## 9.7 Retire or simplify when value disappears

Retirement triggers include no continuing business action, a better deterministic solution, unsupported population change, loss of reliable inputs/labels, harmful consequences, or maintenance costs exceeding benefit. Identify downstream consumers, replace with an agreed fallback, stop jobs/alerts, archive reproducibility evidence according to retention rules, and remove obsolete access/dependencies. Record why the system ended and what evidence would justify a new project.

The lifecycle can end successfully with 'keep the existing rule', 'collect data first', or 'retire the model'. Production ML is justified by continuing useful decisions, not by the existence of a model artifact.
