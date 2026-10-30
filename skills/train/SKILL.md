---
name: train
description: Review model choices, Optuna or Bayesian hyperparameter searches, small tuning budgets, and final refitting, calibration or threshold reuse. Use for training plans and measured fitting failures; resolve missing evaluation boundaries before fitting.
---

# Earn a model choice with evidence

For design-only reviews, load relevant methodology without project-state or notebook files. Resolve links relative to this directory, preserving `../`. Do not invent API names or provide code that has not been checked. Repeated entities require an explicit known-versus-unseen entity claim before choosing grouped or temporal splits. Similar candidate scores do not prove irreducible noise.

Verify the task, source identity, split/metric contract, budget, and candidate-compatible pipeline specification using [state](../../references/project-state.md). Resolve unsupported design with [evaluation](../evaluation/SKILL.md). Consult [capabilities](../../references/capabilities.md) before promising specialist execution.

## Choose relevant detail

- Choosing baselines, linear/nonlinear candidates, count/exposure domains, or dimensionality/resource approaches: read [candidates](references/candidates.md).
- Search strategy, Bayesian optimization/Optuna, pruning, learning curves, or measured failures: read [search and diagnosis](references/search-diagnosis.md).
- Selecting the final procedure, calibrating, choosing thresholds, refitting on more data: read [final fitting](references/final-fitting.md).
- Forecasting, ranking, censored/causal or other specialist task: load its [profile](../../references/tasks/index.md) before applying generic supervised assumptions.

## Compare and diagnose

Start with a meaningful simple/business baseline and a small justified candidate set. A linear model can use nonlinear feature expansions; skew or a failed normality test does not decide model nonlinearity. Check response domain, exposure, annotation, sample support, and memory before allocating search budget.

Use consistent valid evaluation conditions and fold-local preprocessing. Ask [prepare](../prepare/SKILL.md) for missing representations. Fit baselines before expensive tuning. Search only consequential parameters within defensible ranges; record objective direction, folds, seeds, budgets, failed trials, pruning, and environment. Optuna automates proposal/evaluation bookkeeping; it cannot define the right objective or repair leakage. Optional libraries are project dependencies, not silently installed plugin startup requirements.

Budget actual fits, including diagnostic refits and nested parallel workers. Allocate workers at one layer (folds or estimator) and cap the other layers unless measured resource limits support nesting. Count revised configurations against the search budget, retaining earlier results. When later checks need out-of-fold predictions, save aligned predictions, probabilities, fold membership and candidate IDs during the initial fits, or retain those fitted fold estimators. Reuse that evidence where the evaluation design permits; calling another CV helper normally fits again. Derive tables and labels from one metric record, with an explicit selection rule and tie handling.

Investigate measured failure at the relevant boundary. Distinguish data/split issues, implementation/numerical failures, selection noise, high variance, insufficient signal, and operational infeasibility. Do not repeat larger searches to conceal inconclusive evidence. Preserve failed trials and negative results. Independent/outer evidence evaluates the selected procedure; the best development score is not deployment evidence.

## Final artifact and next path

Select the supported tradeoff, or retain the baseline/reframe/collect data. Define refit, probability/interval calibration, and decision-policy order before final evaluation. Changed base-model scores can invalidate old calibration and thresholds. Record the exact evaluated bundle and distinguish it from any later all-data refit.

For a saved model, define custom transformers once in importable project modules and include them in the bundle; notebook-local or later-redefined classes are not portable dependencies. Before handoff, reload the saved full pipeline in a fresh process and compare predictions on the same raw inputs. Same-kernel reload alone cannot verify portability. See [artifact portability](references/final-fitting.md#artifact-portability).

Save reproducible experiment code, comparisons, artifact/version references, uncertainty, limitations, and rationale in the [notebook](../../references/notebook-protocol.md). Send a frozen supported candidate to [validate](../validate/SKILL.md). Return source defects to [data](../data/SKILL.md), unsupported claims to [frame](../frame/SKILL.md), and changed boundaries to evaluation. Completion may be `retain_baseline`, `inconclusive`, or `collect_data`; do not manufacture a winning model.
