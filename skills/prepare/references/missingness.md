# missingness

## 5.1 Separate corrections from learned transformations

Correct a confirmed unit/parser/source error using a documented rule. Preserve raw values and provenance. Learn imputation statistics, encodings, vocabulary, scaling, projections, feature selection, and other data-derived parameters inside the training procedure. Apply the fitted procedure unchanged to validation and serving inputs.

Choose transformations jointly with model candidates. A scaled sparse linear pipeline and a native-categorical tree pipeline can legitimately prepare the same inputs differently. `Pipeline` and `ColumnTransformer` support composition, but column routing, output shape, sparse/dense behavior, and metadata still need checks. [Composite estimators](https://scikit-learn.org/stable/modules/compose.html)


## 5.2 Missing data: mechanism, meaning, and model capability

### When does preprocessing happen relative to splitting?

**Default:** define the split first, fit learned preprocessing on training data, and apply the fitted transformations to validation/test. During cross-validation, repeat fitting inside each training fold. Finally fit the selected pipeline on the permitted development data, preserving any held-out calibration/test roles.

| Operation | Before or after splitting? | Reason / real exception |
|---|---|---|
| Parse dates/types, convert known units, apply a predefined validity rule | Can occur before splitting | Rule is fixed by schema/domain knowledge rather than estimated from held-out data; retain records/exclusion counts |
| Identify entity groups or exact/near duplicate sources | Inspect before constructing the split | Related examples must not cross the evaluation boundary; choose deduplication versus grouping based on the observation unit |
| Inspect schema, sizes, key multiplicities, and input availability | Before splitting is appropriate | Needed to design the dataset and evaluation; this does not authorize target-guided test exploration |
| Mean/median/mode/KNN/iterative imputation | Fit after splitting, within each training fold | Even an operation using no target can learn the held-out distribution |
| Fill with a genuinely predefined constant such as an explicit categorical missing token | Can be stateless and technically precede splitting | The value and rule must be fixed independently of held-out data; keeping it in the pipeline still ensures serving consistency |
| Scale, learn categories/IDF, PCA, select features, learn outlier cutoffs | Fit after splitting, within each training fold | Estimated parameters and selected representations belong to training |
| Apply an externally fitted frozen transform | Apply after split as part of the pipeline | Do not refit on held-out data; document external provenance and possible overlap with evaluation data |
| Forward-fill or construct lags | Follow historical availability, not just file order | A value genuinely known before a later prediction can be used; interpolation/backfill from its future cannot be used for real-time prediction |

These exceptions do not justify filling from whole-dataset averages. For example, two candidate pipelines must each learn their median on the same training fold, not share a median calculated once before CV. A preprocessing pipeline is the practical default even for stateless operations because it preserves train/serve behavior. [Training-only preprocessing](https://scikit-learn.org/stable/common_pitfalls.html)

Missing **features** and missing **labels** require different actions. Feature imputation may be appropriate. An unobserved outcome must not become a negative label or be mean-filled to make supervised evaluation possible; collect/mature it, use a justified censored/weak-label route, or limit the analysis explicitly. See [label design](../../evaluation/references/labels-splits.md).

Ask why each value is missing, whether it will be missing at inference, and whether missingness itself reflects an available signal. Distinguish not measured, unavailable yet, not applicable, withheld, and failed instrumentation. Under MCAR missingness does not depend on observed/unobserved values; MAR conditions on observed information; MNAR retains dependence on unobserved values. Observed data alone generally cannot prove MAR versus MNAR. Use domain knowledge and sensitivity analysis. [Van Buuren, missing-data mechanisms](https://stefvanbuuren.name/fimd/sec-MCAR.html)

| Situation | Candidate handling | Evidence and failure path |
|---|---|---|
| Confirmed collection/parser failure | Repair upstream and rebuild | Compare corrected counts and downstream population; do not disguise it with imputation |
| Feature absent for everyone at prediction | Remove or redesign availability | Training completeness cannot make an unavailable input usable |
| Few missing numeric values, simple baseline | Median/mean imputation, optionally indicator | Compare under intended missingness; proportion alone is not justification |
| Categorical missingness has meaning | Explicit missing category or justified mode | Keep unknown category distinct where semantics require it |
| Estimator supports missing values natively | Compare native route | Verify exact estimator/version and entirely missing columns |
| Similar observations can inform values | KNN imputation | Scale meaningful distances; inspect dimensionality, missing overlap, and cost |
| Other variables strongly inform missing values | Iterative multivariate imputation | Model assumptions, bounds, convergence, computation, and leakage |
| Scientific inference requires missing-data uncertainty | Appropriate multiple-imputation analysis | Combine estimates/uncertainty correctly; one filled table understates uncertainty |
| Dropping rows/columns considered | Sensitivity comparison and coverage audit | Selection bias, information loss, unsupported groups; never a fixed percentage rule |

Simple imputation is a useful benchmark, not proof that the mechanism is harmless. Test all-missing columns and missing indicators explicitly because output schema can vary by configuration/version. [SimpleImputer](https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html). KNN uses available-coordinate distances and neighbor values; imputation is not a substitute for meaningful similarity. [KNNImputer](https://scikit-learn.org/stable/modules/generated/sklearn.impute.KNNImputer.html). Iterative imputation models variables in turn; scikit-learn marks its implementation experimental. Its stochastic options do not automatically implement an entire valid multiple-imputation inference workflow. [IterativeImputer](https://scikit-learn.org/stable/modules/generated/sklearn.impute.IterativeImputer.html)

For time series, interpolation using future observations can leak. Determine whether the actual task is retrospective reconstruction or real-time prediction; use past-available fills or model missingness for the latter. Compare performance when an entire source is absent, not only randomly deleted cells.

### Implementation checks for conditional missingness

Keep structural not-applicable and unknown states distinct; an unknown value does not establish MCAR, MAR, or MNAR. A structural numeric placeholder is an encoding choice with an applicability flag, not a factual assertion that the underlying value is zero. Any imputation statistic for an applicable subgroup must be learned from that subgroup's observed values in the permitted training fold.

An applicability flag does not make an ordinary imputer conditional: `SimpleImputer` fills every matching missing value in the columns it receives, and its indicator marks structural and unknown missing values alike. Define subgroup masking/restoration and separate flags explicitly. A linear estimator still needs an accepted finite representation; a companion flag does not make it ignore NaN. Verify the transformed rows for each semantic state before claiming that an implementation matches this specification.

`ColumnTransformer` selectors operate on columns. Conditional row rules belong inside an appropriate transformer, with output rows kept in their original order. Do not pass a row mask as its column selector. [ColumnTransformer contract](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html)

`MissingIndicator` returns a mask, not the original numeric features. Placing it after an imputer loses the original missingness and can replace the feature matrix with an empty mask. Use a separate original-input indicator branch or supported `SimpleImputer(add_indicator=True)` composition; test the output when new columns become missing at inference. [MissingIndicator](https://scikit-learn.org/stable/modules/generated/sklearn.impute.MissingIndicator.html), [SimpleImputer](https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html)
