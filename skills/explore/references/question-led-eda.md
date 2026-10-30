# question led eda

## 4.1 EDA answers questions; it is not a mandatory gallery

Use the training partition for target-guided exploration. Start with the data-generating process and questions raised by ingestion. Choose summaries and plots that resolve those questions. EDA combines graphics and quantitative investigation to reveal structure, anomalies, and possible assumption failures. [NIST EDA](https://www.itl.nist.gov/div898/handbook/eda/section1/eda11.htm)

| Observation or question | Inspect | Possible consequence, subject to validation |
|---|---|---|
| What does one row represent? | Key multiplicity, entity timelines, joins, sampling | Rebuild unit/aggregations or grouped split before modeling |
| Implausible ranges or sudden spikes | Units, raw source, timestamps, batch/source comparisons | Correct confirmed errors; quarantine unexplained values |
| Missingness concentrated by group/time | Null rates, co-missing patterns, collection rules | Repair collection, add indicators, choose imputation, restrict unsupported use |
| Highly skewed values | Quantiles, ECDF/log-scale view, extreme examples | Consider robust loss or transformation when objective/model benefits |
| Relationships look curved | Scatter/smooths, residuals, domain shape | Compare splines/interactions/nonlinear candidates; correlation alone cannot choose |
| Correlated inputs | Correlation blocks, redundancy, conditioning, source lineage | Regularize, combine, or remove costly redundant inputs; preserve predictive interactions |
| High-cardinality category | Counts, unseen-category rate, semantic meaning | Sparse/hashing/regularized encoding or remove identifier shortcut |
| Rare outcome or subgroup | Counts of independent positive/negative units | Wider uncertainty, collection priority, task-specific metrics |
| Temporal changes | Cohort rates, seasonal plots, coverage, collection changes | Time-aware validation, known regime features, redesign if process changed |
| Near-perfect feature/target match | Timing, label construction, workflow metadata | Leakage investigation before celebrating signal |
| Weak relationship everywhere | Label audit, measurement reliability, representation, baseline | Reframe/collect; do not conclude nonlinear modeling will rescue it |

Separate known errors from valid extremes. A rare high-value customer or failure may be precisely the business case of interest. Outlier tests depend on distributional assumptions and can be distorted by multiple unusual points. Flagging is an investigation trigger, not automatic deletion. [NIST outliers](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)

## Choose descriptive statistics for the decision

Correlation, covariance, skewness and kurtosis are tools, not universal lifecycle gates. Select meaningful numeric measurements; exclude arbitrary IDs and category codes from moment-based interpretations. Record the sample/population, units, nonmissing support, missing-data handling and estimator convention. Keep undefined/unstable values visible rather than replacing them with zero.

| Statistic | Useful question / trigger | Interpretation boundary and next path |
|---|---|---|
| Pearson correlation; Spearman for monotonic rank association | Are meaningful numeric inputs redundant or associated; is conditioning/representation worth investigating? | Pearson measures linear association; zero does not exclude nonlinear dependence. Constants are undefined. Inspect scatter/conditional structure and pairwise support; no automatic feature deletion, causal claim or model-family choice. |
| Covariance | Does joint variation in original units matter for a covariance-based model, projection or domain calculation? | Scale and unit dependent; not a comparable feature-importance score. Omit a redundant covariance matrix when standardized association answers the question. Clarify centering, sample weighting and missing-data treatment. |
| Skewness | Does asymmetry/extreme leverage affect a numerical representation, mean-based summary or loss? | Pair with quantiles and a histogram/ECDF. A log transform needs a valid domain and predictive justification; skew alone does not require transforming a feature or choosing a nonlinear model. |
| Kurtosis | Are tail/extreme observations consequential to a variance-sensitive method, risk or inference claim? | Specify Pearson kurtosis (normal reference 3) versus Fisher excess (reference 0), bias correction and support. The fourth moment is sensitive to extremes and may be unstable or not exist; do not use a cutoff to delete observations or infer normality. |

For a manageable numeric table, these can be inexpensive descriptive summaries, but compute them only when interpretable and useful. Visual evidence may already answer the shape question. If a selected statistic changes no decision, do not turn its absence into a failed stage. A formal test needs an estimand and sampling assumptions; a descriptive coefficient alone is not a significance test. See [statistical inference](../../statistics/references/inference.md) when that claim is required.

Definitions and implementation conventions: [SciPy Pearson correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html), [NumPy covariance](https://numpy.org/doc/stable/reference/generated/numpy.cov.html), [SciPy skewness](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html), [SciPy kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html). The routing above is workflow guidance, not a universal threshold supplied by those APIs.

## Visual evidence and decisions

Select charts from the question, data shape and intended decision. For a full predictive notebook, consider outcome support, consequential input distributions, missingness and target relationships; state why any relevant unresolved question is deferred. A narrow schema check or a source without enough observations may legitimately need no chart. Do not impose a fixed number or universal chart list on every task.

| Decision boundary | Useful visual evidence | Interpretation and next path |
|---|---|---|
| Outcome representation and evaluation support | Class counts/rates for classification; histogram or ECDF for continuous/count targets | Report denominators and rare outcomes; route unsupported metrics or response domains to evaluation |
| Missing or poorly covered inputs | Missing fractions plus group/time comparison when collection varies | Distinguish sparse coverage from a known collection rule; use missingness guidance before choosing imputation or collection |
| Numeric scale, skew and extremes | Histogram/ECDF, box plot, or raw-versus-log view where the domain permits | Check units and valid extremes; propose candidate-compatible scaling or transformations for validation, not from skew alone |
| Categorical support and outcome differences | Category counts beside outcome rates or conditional distributions | Keep missing categories visible and show sample counts; investigate tiny groups, confounding and possible identifier leakage |
| Numeric relationships or redundancy | Scatter/hexbin, conditional distributions, or selected correlation blocks | Consider interactions, regularization or nonlinear candidates; correlation alone neither selects a model nor proves causality |
| Time, entities or repeated measurements | Timeline, coverage/cohort plot, or entity frequency/overlap summary | Revisit split and deployment claim before feature/model decisions; use the matching task profile |
| Prediction failures after fitting | Held-out development/OOF confusion or residual plots and relevant slice summaries | Reuse appropriately separated predictions; route observed failures to preparation/training or statistical investigation |

Label axes, units, population, transformations and important category ordering. Report sample counts and missing-value exclusions; avoid treating absent observations as zeros. Use shared scales when comparing panels, disclose sampling and avoid misleading truncation. Fit any learned binning, selection or transformation inside the training folds when it enters the predictive pipeline, even if a descriptive plot used all development rows.

Render the chosen figures into the executed notebook (or link a verified saved figure when required by the environment). Inspect for empty panels, clipped labels, unreadable legends and mismatched denominators. For matrix/heatmap plots, map positional ticks back to the actual row/column labels, especially after sorting or filtering. Fix a discovered label mismatch in the plotting code and rerender the figure; a distant explanatory note leaves the chart misleading when viewed alone. Make the consequential interpretation clear in the caption or nearby discussion; related plots can share one explanation. Avoid repeating labels and values already legible in the figure. Matplotlib supports explicit figure/axes creation, labels and notebook display; choose another installed library when it better serves the task. [Matplotlib quick start](https://matplotlib.org/stable/users/explain/quick_start.html)
