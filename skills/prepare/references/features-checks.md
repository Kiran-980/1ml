# features checks

## 5.6 Feature construction and selection

### Decide whether feature engineering is needed

Separate required schema/semantic corrections, estimator-required preprocessing, optional feature construction, and feature selection. They answer different questions. Always make the feature-construction decision explicit for a full predictive project; adding features is optional.

| Evidence / condition | Decision path | Evidence before claiming value |
|---|---|---|
| Existing available columns express the needed information and the baseline meets the task | Keep the basic representation; no new features for their own sake | Record validation and cost/coverage evidence supporting no additional engineering |
| A domain-supported signal is poorly represented: ratio, exposure, recency, interaction, missingness, periodicity | Propose a small feature set with source columns, definition, prediction-time availability and failure handling | Compare the basic and engineered representation with the same estimator, folds and metric when budget permits |
| The estimator already captures the suspected relationship | Treat explicit construction as optional, not automatically useful | Assess validation gain, stability, cost or interpretability rather than assuming trees remove all feature-engineering needs |
| Candidate relies on future values, target leakage, unstable IDs or unavailable inputs | Reject or redesign before fitting | Availability/lineage check; target-derived features require valid cross-fitting |
| Feature construction is plausible but no isolated comparison fits the budget | Label it a hypothesis or pragmatic representation; defer its incremental-gain claim | Record the missing ablation and next comparison; a good score for the combined pipeline does not prove the feature was necessary |
| Errors suggest label/source failure rather than representation weakness | Return to data or evaluation | Repair the measured failure before generating more features |

In the notebook, use a compact decision table: source columns/evidence → proposed feature or no-change → reason/availability → comparison/check → retain/reject/defer. Reserve a meaningful representation comparison within the experiment budget when feature gains are central to the task; do not silently exceed it. Keep candidate comparisons comparable and final-test data outside feature selection. After final evaluation, do not reopen engineering against those results without renewed evaluation.

Build features from domain hypotheses: rates with denominators, historical recency/frequency, interactions, cyclic time encodings, text representations, spatial summaries, or physically meaningful ratios. Guard zero denominators and distinguish age at prediction from age today. Lag/rolling windows must end at the prediction boundary; current global aggregates can leak future records.

Assess value against acquisition cost, availability delay, missing-source resilience, stability, and predictive gain. An expensive sensor or private attribute may be unjustified for a negligible gain. Correlated features may be redundant for prediction while each matters causally; use the task to decide.

Feature selection options include domain exclusions, constant-feature removal, univariate screening, regularized embedded selection, model importance, and wrapper search. Univariate screening can miss interactions; wrapper search is expensive; importance is estimator-dependent. Include selection inside validation and compare against keeping all feasible inputs. [Feature selection](https://scikit-learn.org/stable/modules/feature_selection.html)

Dimensionality reduction transforms inputs rather than selecting original columns. PCA maximizes represented variance, which need not be predictive signal; scale choice changes that variance. Truncated SVD supports uncentered sparse matrices. NMF requires nonnegative inputs and offers additive components. Choose dimension by downstream validation and resource constraints, not explained variance alone. [Decomposition](https://scikit-learn.org/stable/modules/decomposition.html)


## 5.7 Preprocessing acceptance checks

Exercise the fitted pipeline on ordinary, missing, unknown-category, reordered-column, all-missing-feature, extreme, sparse, and empty/bad-schema cases as appropriate to the input contract. Assert stable feature order/types, preserved row/label alignment, and outputs valid for the receiving estimator: intentional missing markers may remain for native-missing-value models, while unexpected NaN/infinity or domain violations must be detected. Preserve feature names and transform versions for inspection.

Proceed when each transformation has a data/model reason and a reproducible train/serve implementation. If it only improves a leaked split or hides a collection fault, return to [data](../../data/SKILL.md) or [evaluation design](../../evaluation/references/labels-splits.md). Model comparisons must include their complete preprocessing pipelines.


## 5.8 Transformation order and genuine scope exceptions

There is no one correct transform chain for every estimator. Resolve semantic errors/missing markers first, then choose ordering from the downstream mathematical requirements and production contract:

| Interaction | Required reasoning |
|---|---|
| Simple numeric imputation and scaling | Impute then scale is a straightforward candidate. Fit both in the training fold; compare with a native-missing route where supported. |
| Distance-based imputation | Distances may require scaling before neighbor selection. Use a fitted scaler that accepts the missing markers or another explicitly supported distance design; check observed-coordinate behavior and all-missing columns. |
| Log/power transform and imputation | Ensure valid domains at each step. Imputing before versus after a nonlinear transform is not generally equivalent; choose from semantics and validation, not API convenience. |
| Resampling with distance/categorical structure | Apply the representation/metric the sampler expects inside training only. Preserve categorical validity and use a sampler-aware pipeline; ordinary prediction must not resample arriving requests. |
| Nonnegative method after centering | Centering can create negative values incompatible with NMF or some count-based learners. Change the representation or estimator rather than silently clipping away information. |
| One-hot inputs with an unregularized full-rank linear design | Address intercept/category redundancy deliberately. A regularized model need not use the same dropping convention; test unknown-category interpretation and preserve the fitted mapping. |
| Native missing/categorical model | Preserve supported dtypes and missing markers. A universal impute/scale/encode block may remove the very capability being compared. |

These are synthesis checks using the transformer/method references above. Validate the actual chain and nested fitting boundary in [chapter 3](../../evaluation/references/inner-validation.md#37-inner-validation-must-respect-the-outer-design), rather than validating each component only in isolation.

For target transforms, encapsulate training transformation and prediction inversion together. A wrapper such as `TransformedTargetRegressor` handles that fit/predict relationship; it does not automatically correct retransformation bias or choose the business estimand. Score on the required original scale and check the output domain. [Target-transform wrapper](https://scikit-learn.org/stable/modules/generated/sklearn.compose.TransformedTargetRegressor.html)

Learn clipping/winsorization cutoffs from training data when they are estimated; keep fixed physically justified limits distinct. Evaluate the declared deployment population, including valid extremes and failed/rejected cases. Removing high-residual test cases or choosing cutoffs after seeing test improvements changes the evaluation and cannot be presented as neutral cleaning.

Two legitimate scope exceptions need explicit labeling. **Descriptive/inferential analysis of the observed sample** may use that sample in full under its statistical design; do not force a predictive holdout where no predictive claim is made. **A deliberately transductive task** may use the unlabeled feature pool it is designed to infer over, with labels withheld appropriately; this does not establish performance on arbitrary future points. Keep an inductive evaluation separate when that future-point claim is required. See [prediction versus inference](../../statistics/references/inference.md#42-distinguish-prediction-description-and-inference) and [semi-supervised learning](../../../references/tasks/scarce-labels.md#few-labels-semi-supervised-and-active-learning). These exceptions do not permit ordinary predictive preprocessing to learn from a reserved test set by default.
