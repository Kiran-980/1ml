# representations

## 5.3 Scaling, normalization, and transformation are different operations

| Operation | When to compare it | Important limitation |
|---|---|---|
| Standardization: training mean/std | Regularized linear models, SVM, neural nets, many distance methods | Does not make data normal; outliers influence estimates |
| Robust scaling: median/interquartile range | Scale-sensitive models with valid extreme values | Does not remove outliers or guarantee robust predictions |
| Min-max scaling | Bounded representation or model requirement | New observations can exceed the training range; sensitive to extremes |
| Max-absolute scaling | Sparse features when preserving zeros matters | Extreme magnitudes still set scale |
| Per-row unit norm | Direction/similarity matters more than magnitude, often text vectors | Removes magnitude information; inappropriate if magnitude is predictive |
| Log/power transform | Domain supports multiplicative or skewed relation | Changes distances and functional form; evaluate original task loss |
| Quantile mapping | Distribution shaping has empirical benefit | Nonlinear distortion, tail saturation, loss of original distances |
| No scaling | Tree splits or a naturally meaningful common scale | Other pipeline components may still require scaling |

Centering sparse matrices can destroy sparsity and memory feasibility; use an appropriate sparse-compatible configuration. Fit scaling parameters on training data. [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html). RobustScaler uses robust location/range statistics but has the same need for a model-level validation comparison. [RobustScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html)

Box-Cox requires strictly positive values; Yeo-Johnson supports signed values. An arbitrary offset changes meaning and should not be inserted only to satisfy an API. [PowerTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PowerTransformer.html). Row normalization, scaling, and quantile transforms serve different purposes and must not be bundled under 'normalize everything'. [Preprocessing reference](https://scikit-learn.org/stable/modules/preprocessing.html)

Target transformations require separate reasoning. Optimizing squared error in log space is not optimizing squared error on the original amount. Naive inverse transformation generally does not recover the original-scale conditional mean; choose a justified retransformation/model and score the actual business objective.


## 5.4 Categories and text

| Representation | Appropriate branch | Check |
|---|---|---|
| One-hot | Unordered categories, manageable sparse width | Unknown/missing/infrequent categories, stable vocabulary, output dimensions |
| Ordinal | Genuine order or estimator-specific categorical interface | Numeric codes must not accidentally impose false distances/order |
| Frequency/count | Useful prevalence signal without labels | Fit within fold; shifting population frequencies |
| Target encoding | High cardinality and enough support for regularization | Out-of-fold construction, smoothing, group/time leakage, unseen fallback |
| Hashing | Streaming/huge vocabulary, fixed dimension | Collisions, sign/nonnegative constraints, reduced interpretability |
| Native categorical learner | Supported tabular model/version | Cardinality constraints, category codes, unknown/missing behavior |
| Learned/frozen embeddings | Semantic similarity or transfer | Domain mismatch, version, cost, evaluation and source rights |

One-hot `handle_unknown='ignore'` creates an all-zero vector for unknown categories; an infrequent category route exists only when configuration/training created one. Explicitly test this at serving. [OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)

Target encoding can leak a row's own outcome. Scikit-learn's `fit_transform` uses cross-fitting and differs from `fit().transform()` on training data. Current documentation supports configurable CV; inspect installed-version capabilities. Group/time settings need a valid scheme: ordinary random cross-fitting can still leak entities or future labels, and temporal splits may not partition all training rows. Design an explicit history-only fallback for early rows. [TargetEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html)

For text, compare sparse counts/TF-IDF with simple linear or suitable Naive Bayes baselines before expensive adaptation. Tokenization, case, punctuation, negation, and document metadata can affect the target; blanket cleaning may remove signal or preserve shortcuts. Fit vocabulary/IDF inside training. Specialized text evaluation continues in [chapter 7](../../../references/tasks/index.md). [Feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)


## 5.5 Class imbalance and unequal observation importance

First decide whether imbalance reflects deployment, sampling, or mislabeled outcomes. Fix evaluation and policy before changing training prevalence. Compare unmodified loss, class/sample weights, threshold changes, and justified resampling as separate experiments. Costs and class frequencies are different quantities.

Resample only the training partition within each fold. Preserve natural deployment prevalence in evaluation or explicitly correct the evaluation design. Whole-dataset resampling can leak neighbors and distort test distribution. [Imbalanced-learn pitfalls](https://imbalanced-learn.org/stable/common_pitfalls.html)

SMOTE-type methods interpolate neighbors; they may create invalid combinations for categories, sparse text, temporal sequences, or constrained measurements. Categorical variants exist, but do not establish semantic validity by themselves. Oversampling duplicates does not create independent evidence; undersampling may discard useful negatives. Validate rare subclasses, calibration, and review workload. [Oversampling methods](https://imbalanced-learn.org/stable/over_sampling.html)

Sample weights can mean population sampling correction, exposure, reliability, or decision costs. Record the meaning and which fitting/scoring components receive them. A single weight vector cannot automatically stand for all four purposes.
