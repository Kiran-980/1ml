# search diagnosis

## 6.5 Design the training experiment

Write a hypothesis, candidate pipeline, expected benefit, metric/constraint, split, budget, and stopping rule. Log data and code versions, environment, features, seeds, all parameters including defaults, compute, duration, warnings, failures, metrics, and artifacts. Record failed runs as failures rather than dropping them from the comparison. [MLflow tracking](https://mlflow.org/docs/latest/ml/tracking/)

Check label alignment, tensor/array dimensions, valid feature domains, scorer direction, and baseline predictions with a small smoke fit. A successful fit only establishes execution. Investigate convergence warnings: scaling, conditioning, solver/loss compatibility, and iteration budget may matter. More iterations are justified only if optimization has not stabilized and the budget permits it.

Deep-learning branches additionally need train/eval mode correctness, batching/shuffling appropriate to the task, optimizer schedule, checkpoint selection, reproducible preprocessing, and task-valid augmentation. Monitor loss behavior and selected validation metrics; keep the test set out of checkpoint selection. A seed is useful provenance but does not guarantee identical results across every backend/device/version.


## 6.6 Tune only what the evidence and budget justify

Use meaningful parameter ranges, often logarithmic for regularization/learning rates, with conditional spaces for compatible settings. Start with influential parameters; compare search strategies according to cost. Random search can cover broad spaces; grid search is useful for small targeted spaces; successive halving depends on early-resource performance being informative. Search includes preprocessing and feature choices when those are learned design decisions. [Hyperparameter search](https://scikit-learn.org/stable/modules/grid_search.html)

Use the selected splitter inside tuning. Built-in random early-stopping partitions may violate group/time assumptions; inspect implementation and provide an appropriate validation design or disable that shortcut. Select iteration/checkpoint counts without test access. Refit according to the locked selection procedure and retain any independent calibration/evaluation roles.

Manage nested parallelism and memory: parallel folds, estimator threads, and BLAS/OpenMP can oversubscribe the same machine. Benchmark wall time and peak memory on a representative subset; set limits accordingly. [Parallelism](https://scikit-learn.org/stable/computing/parallelism.html)


## 6.7 Bayesian optimization and Optuna

Bayesian optimization models the relationship between hyperparameters and objective outcomes, then uses an acquisition strategy to select informative/promising trials. The surrogate is a model of the **search objective**, not necessarily the final predictive model. A Bayesian optimizer can tune a random forest, SVM, or neural network; it does not require Bayesian predictive modeling. The original practical GP-based work also considers varying evaluation costs and parallel trials. [Snoek, Larochelle, and Adams](https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html)

| Search situation | Reasonable comparison | Why / caution |
|---|---|---|
| Tiny finite space, few cheap trials | Grid or exhaustive search | Easy coverage; surrogate overhead may offer little benefit |
| Broad initial baseline, many parallel cheap trials | Random search | Simple, robust benchmark; does not learn from trial history |
| Expensive trials and a modest effective search dimension | GP-based Bayesian optimization | Can use past results efficiently; surrogate/acquisition overhead and assumptions matter |
| Mixed categorical/conditional model configuration | TPE-based sequential search | Useful concrete candidate for structured spaces; validate actual sampler support |
| Iterative training with informative intermediate quality | Search plus pruning/multi-fidelity strategy | Early scores must be comparable and predictive of final quality |
| Extremely noisy validation or very few independent events | Improve evaluation before aggressive search | Optimization otherwise selects noise more efficiently |
| Many objectives/constraints | Supported multiobjective/constrained search | Return feasible tradeoffs; do not invent a single score without business rationale |

Optuna supplies samplers and separate pruners. Sampling chooses a configuration; pruning stops an unpromising trial early. Neither replaces correct evaluation. Use installed-version documentation for sampler/pruner compatibility, especially multiobjective studies. [Optuna algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html)

`TPESampler` models distributions of parameter values associated with better and remaining outcomes, then proposes promising values. It has startup trials and options for joint/conditional behavior; it is not a Gaussian-process surrogate. Record the explicit sampler/configuration instead of depending silently on a framework default. [TPE reference](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)

`GPSampler` fits a GP and optimizes an acquisition function; its noise setting, dependencies, constraints, and parallel capabilities depend on the version. Only mark the objective deterministic when repeated evaluation of the same configuration under the stated protocol is deterministic. The observed CV score may still estimate population performance imperfectly even when rerunning it gives the same number. [GP reference](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.GPSampler.html)

**1ml study design:**

1. Fix the dataset version, group/time-aware inner folds, objective direction, aggregation, baseline, resource budget, and stopping rule. Keep the final test outside the objective entirely.
2. Define parameters that can plausibly matter, with type/domain/log-scale and conditional activation. For example, suggest kernel width only for the kernel branch, and choose a valid penalty/solver combination rather than letting incompatible trials dominate the budget. [Optuna search spaces](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html)
3. Each trial constructs and fits a complete pipeline independently inside every training fold, including imputation, encoding, selection, and resampling. Aggregate validation results according to the metric contract, not whichever average looks best.
4. Use the same comparison folds across trials. For stochastic fitting, record seeds and variability; reassess promising candidates across appropriate seeds/folds instead of treating one lucky run as a stable gain. To estimate the entire selection procedure with less selection optimism, use an appropriate outer evaluation. Nested CV does not remove sampling uncertainty, population mismatch, or every source of bias.
5. Set trial/time limits and memory/concurrency controls. Compare search methods by the budget relevant to the project, such as wall-clock/compute cost; equal trial counts can conceal very different trial costs.
6. Prune only when reported intermediate values have comparable meaning. Epoch-based reports need consistent validation; fold-based pruning can be biased if early folds systematically differ from later ones. Slow-learning candidates may be unfairly discarded. Keep adequate warm-up and verify the pruning policy experimentally.
7. Store complete/pruned/failed states, failure reasons, parameters, fold metrics, duration, and dataset/protocol identity. A crashed fit is not a legitimately poor numeric score. Resume a study only when its data/objective/search-space semantics remain compatible; create a new study for materially changed evidence.
8. Select within the feasible region, reassess stability, then refit and independently evaluate the locked procedure. Keep calibration/threshold fitting roles intact. The study's best validation score is a selection result, not the final generalization claim.

**Failure routes:** If every trial is invalid, debug configuration/domain handling before increasing budget. If improvements vanish across seeds or outer folds, improve evaluation or reduce search flexibility. If the surrogate overhead exceeds training time, use a simpler search. If trial durations vary dramatically, compare cost-aware policies and scheduling rather than assuming serial BO is always fastest. Parallel asynchronous completion can change the search trajectory even with a sampler seed.

No hyperparameter framework guarantees a global optimum or prevents validation overfitting. Use Optuna as an implementation option for the future training skill, not an unconditional dependency for every project. This research pass does not install it or run a study.


## 6.8 Diagnose measured failures before choosing a remedy

| Evidence | Plausible explanations | Next discriminating action |
|---|---|---|
| Poor train and validation scores | Weak features/labels, restrictive model, failed optimization, hard task | Verify baseline, learning/convergence, label audit; compare one targeted feature/model change |
| Strong train, weak validation | Overfitting, leakage in training assessment, split mismatch | Audit split; regularize/simplify; compare learning curves and representative data |
| Huge variation between folds | Small event support, group heterogeneity, drift, unstable fitting | Inspect counts/time/groups and seeds; reconsider claim and uncertainty |
| Good average, weak critical slice | Coverage, label quality, representation, threshold mismatch | Slice error audit, targeted collection, constrained policy or reduced scope |
| Good ranking, bad probabilities | Calibration or population shift | Independent calibration analysis; inspect sampling/weighting |
| Good offline, poor production | Train/serve mismatch, delayed labels, policy feedback, shifted population | Replay actual pipeline inputs, compare schema/features and matched cohorts |
| All complex methods barely beat baseline | Weak signal, irreducible noise, incorrect target/action | Reframe or acquire better evidence; retain non-ML baseline if adequate |
| Suspiciously perfect validation | Leakage, duplicates, target proxy, scoring bug | Audit provenance/timing and run negative controls before accepting |

These are hypotheses, not diagnosed causes. Change one suspected factor at a time and retain evidence that supports the conclusion. Learning curves can guide the investigation but do not uniquely identify the cause. [Learning-curve diagnostics](https://scikit-learn.org/stable/modules/learning_curve.html)
