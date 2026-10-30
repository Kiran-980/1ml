# labels splits

## 3.1 Define labels before splitting

Label construction applies when the task has outcomes or annotations. Unsupervised tasks still need an evaluation design for their intended stability, usefulness, or new-data claim; they do not require invented labels. Descriptive/inferential questions use the relevant sampling and uncertainty design instead of a mandatory predictive holdout. Resolve specialized task assumptions before selecting a generic splitter.

Write the prediction timestamp, feature lookback, outcome window, and label maturation delay. For a 30-day outcome, yesterday's record usually cannot yet have a confirmed negative label. Separate unknown/unobserved from negative. If observation ends early, use an appropriate censoring treatment or restrict to fully observed outcomes with a documented population consequence.

Audit label sources for policy effects, disagreement, duplicate events, retrospective edits, and proxy mismatch. Chargebacks may arrive long after a transaction; fraud detected under the old policy may omit uninvestigated fraud. A label can be accurate for its collection process and still be biased for deployment. Record that uncertainty rather than silently imputing negatives.


## 3.2 Match the split to the generalization claim

| Deployment claim | Split/design | Failure it prevents |
|---|---|---|
| New independent records from a stable population | Random holdout or suitable CV; stratification if useful | Accidental class depletion, while preserving the intended population |
| New patient/customer/device/site | Group-disjoint split | Memorizing an entity present in both sides |
| Future outcomes for existing entities | Chronological/rolling-origin split | Training on future patterns or revised history |
| New entities in a future period | Combined group and temporal design | Passing one generalization test while failing the other |
| Nearby geography or related networks | Spatial blocks/buffers or graph-aware design | Dependence across nearby/connected observations |
| Multiple crops/windows/augmentations of one original | Split original source first | Near-duplicate leakage |
| Query/session ranking | Keep evaluation units coherent; use time if deployment is future | Fragmented queries and future feedback |
| Model/hyperparameter selection with limited data | Inner selection and outer evaluation | Optimism from reporting the same CV used for selection |

Stratification balances labels; it does not make dependent observations independent. Grouped splitting tests unseen groups, which may differ from forecasting more records for known groups. Choose the claim first, then the splitter. [Cross-validation design](https://scikit-learn.org/stable/modules/cross_validation.html)

For tomorrow's transactions from existing customers, customer overlap with earlier training history is expected: use chronological evaluation and account for customer dependence in uncertainty. A customer-disjoint test answers a separate new-customer question; do not silently substitute it. At each historical training origin, include only labels actually available then. Evaluate later predictions after their outcomes mature using an explicit observation/as-of timestamp, not the maximum transaction timestamp as a proxy for data completeness. Reporting delay and the outcome definition are separate: a 60-day reporting delay does not itself define a 60-day outcome. Split code must implement time boundaries, not merely assert a gap after randomly assigning customers.

Temporal validation must mimic the prediction horizon, feature lookback, training update schedule, and outcome maturation. A gap may be needed when training labels overlap the validation period or when availability delays require it; there is no universal embargo length. `TimeSeriesSplit` provides expanding partitions and a gap parameter, but it does not automatically encode all these semantics. Equal spacing matters for comparable fold durations; irregular events may need explicit timestamp-based splits. [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)

Its `gap` and `test_size` are sample counts, not calendar durations; `test_size='30D'` is not its API. For event data, specify timestamp predicates and label-availability cutoffs, then implement and verify those memberships. In a design-only answer, those predicates are more useful than an unverified splitter code sketch.


## 3.3 Allocate roles, not magic percentages

Training fits parameters. Validation selects features, transformations, hyperparameters, thresholds, and early-stopping settings. Calibration fits probability/interval adjustments where needed. The final test evaluates the locked procedure. These roles can be arranged through cross-fitting/nested designs rather than four fixed physical partitions, provided the independence requirements are preserved.

Choose allocation from event counts, uncertainty, dependence, drift, and training needs. A universal 80/20 rule may leave too few events for a useful test. With scarce data, repeated/nested CV may help characterize variability, but correlated folds are not independent new datasets and repeated use cannot manufacture external validity.

Freeze a split manifest with stable row/group identifiers, time boundaries, exclusions, seed, and dataset version. Evaluate competing candidates on comparable observations. Ensure classes and required groups have enough support; if a fold lacks positives, report undefined metrics and redesign evaluation rather than silently replacing them with zero.


## 3.4 Leakage audit by boundary

| Boundary | Inspect | Correction |
|---|---|---|
| Feature availability | Outcome flags, resolution codes, future aggregates, late-arriving data | Remove or reconstruct strictly historical values |
| Entity/source identity | Repeated subjects, duplicate files, template copies | Group, deduplicate with domain rationale, or redefine claim |
| Learned preprocessing | Global imputation, scaling, PCA, vocabulary, feature selection | Fit within each training fold |
| Target-derived encoding | Target means that include the row or future labels | Out-of-fold/time-respecting encoding |
| Resampling/augmentation | Synthetic neighbors or transformed copies crossing splits | Split first; resample training only |
| Search/early stopping | Test-informed tuning or repeated test inspection | Use validation; obtain fresh evaluation if the test becomes development data |
| Historical systems | Features computed with current corrected tables | Rebuild using retained historical vintages or disclose unavailable evidence |
| Evaluation population | Easy cases only, omitted failures, model-generated ground truth | Evaluate the full intended workflow and report exclusions |

Pipelines help contain learned transformations but cannot repair a post-outcome input, invalid group split, or a target definition that encodes the answer. [Common leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)


## 3.5 Gate and invalidation

Proceed to training-data EDA when label semantics and observation timing are documented, split membership is reproducible, dependencies are handled, and the evaluation sample supports the intended claim. If historical availability or group identity is unknown, record a bounded provisional analysis and acquire the missing evidence before making deployment claims.

Changing the target, population, prediction horizon, split, or label collection process invalidates downstream comparisons. A final test used to guide changes becomes development evidence. Preserve its results honestly and establish a new evaluation plan rather than renaming it untouched.
