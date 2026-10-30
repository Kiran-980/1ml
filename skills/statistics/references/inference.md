# inference

## 4.2 Distinguish prediction, description, and inference

For prediction, the central question is performance on the intended unseen population. For inference, the question is an estimand and its uncertainty under sampling/model assumptions. Descriptive summaries characterize observed data and need not imply either. A model can predict well with unstable coefficients; a scientifically interpretable coefficient needs a suitable design and assumptions beyond a validation score.

Before a test, specify the estimand, null and alternative, independent unit, sampling/assignment design, missing-data handling, meaningful effect, and error control. If these are unclear, a p-value is premature. EDA can generate hypotheses; testing those on the same data as if prespecified overstates evidence. Mark exploratory results and validate important discoveries separately.


## 4.3 Central limit theorem: what it does and does not establish

Under the classical independent, identically distributed, finite-variance setting, the standardized sample mean approaches a normal distribution as sample size increases. The raw observations do not thereby become normal. The theorem concerns repeated-sample behavior of an estimator. There is no universal 'n >= 30' guarantee: skew, heavy tails, rare events, dependence, and the requested tail accuracy matter. [NIST CLT definition](https://csrc.nist.gov/glossary/term/central_limit_theorem)

Practical routing: identify the independent unit; inspect the estimator and tail behavior; use a justified analytical approximation or resampling/design-specific method. Ten thousand visits from a hundred users are not ten thousand independent users. Strong dependence requires a cluster/time-aware analysis, not an appeal to large row count. Infinite-variance examples fall outside the classical finite-variance theorem.

Normality is not a generic requirement for ML features. Standardization does not make a distribution Gaussian. Linear-model inference often involves assumptions about errors conditional on inputs, not the marginal distribution of every input. Logistic regression does not require normally distributed predictors. A/B testing does not require a particular training algorithm to be normally distributed.


## 4.4 Select statistical comparisons by design and estimand

| Question/design | Candidate method | Check before interpreting |
|---|---|---|
| Mean difference between independent groups | Welch t interval/test where justified | Independent units, mean is desired, heavy-tail/small-sample sensitivity |
| Mean change for paired units | Paired analysis of within-unit differences | Correct pairing, independence across pairs, behavior of differences |
| Distributional ordering without a Gaussian model | Mann-Whitney for independent samples; suitable paired rank method for paired data | Rank tests are not assumption-free and are not generally tests of equal medians |
| Association in category counts | Chi-square independence; exact/resampling alternatives for sparse designs | Counts rather than percentages, expected counts, independence, fixed-margin assumptions |
| Linear association | Pearson coefficient with justified uncertainty | Outliers, nonlinear patterns, range restriction, dependence |
| Monotonic association | Spearman/rank-based analysis | Ties, sampling dependence, monotonic rather than arbitrary nonlinear relationship |
| More than two groups | Appropriate ANOVA/Welch/model-based or rank-based design | Unequal variances, repeated measures, planned contrasts, multiplicity |
| Repeated/grouped measurements | Cluster-aware inference, mixed models, GEE, or design-based analysis | Group structure, enough independent groups, target population |
| Time-dependent observations | Time-series/model-based or block-resampling analysis | Serial dependence, trend/seasonality, stationarity assumptions where required |
| Practical equivalence/noninferiority | Prespecified margin and appropriate interval/test | Failure to find a difference is not evidence of equivalence |

Welch's test relaxes equal-variance assumptions for two independent means; it does not fix dependence or biased sampling. [SciPy t-test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html). Mann-Whitney's location interpretation requires stronger conditions than simply having ranks. [Mann-Whitney](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html). Contingency-table methods operate on observed counts with a specified null sampling model. [Chi-square](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html). Pearson measures linear association, not causation or all forms of dependence. [Pearson correlation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html). Equivalence tests explicitly require lower/upper margins. [TOST](https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.ttost_ind.html)

The table is a routing aid. Fetch the exact method's assumptions and implementation for the actual design before execution; especially for censored, clustered, weighted, sparse, or sequential data, a familiar default test can answer the wrong question.

For a multistage survey, derive each observation's inclusion probability across stages. Unequal school selection probabilities can cancel against within-school sampling fractions; do not assert unequal final weights without that calculation. Record strata, sampling with/without replacement, joint inclusion information or an appropriate variance approximation, finite-population corrections, and nonresponse. Few primary units limit uncertainty estimation. BRR needs its design conditions (typically two primary units per stratum); neither BRR nor an ordinary two-stage bootstrap is a universal small-cluster remedy. Use verified survey tooling such as R's `survey::svydesign`/`svymean` when appropriate, not an invented `statsmodels.survey` API. [Survey package design and replicate-weight documentation](https://cran.r-project.org/web/packages/survey/survey.pdf)


## 4.5 Uncertainty, significance, and repeated searching

Report effect sizes and intervals in decision-relevant units alongside any test. A p-value is not the probability that the null is true, the probability of replication, or the economic value of an effect. Small p-values can accompany trivial effects in large samples; large p-values can accompany poorly measured important effects.

For bootstrap intervals, resample the independent unit and preserve paired predictions when comparing models. Ordinary row bootstrap is inappropriate for dependent rows without a justified dependence-aware design. A bootstrap of fixed held-out predictions captures evaluation-sample variability, not all model-training/selection variability. Rare events and degenerate samples can make intervals unstable. Record method, resamples, random seed, and failure handling. [SciPy bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)

Permutation tests require a valid exchangeability/randomization scheme under the null. Shuffling arbitrary time points, users across incompatible strata, or paired outcomes independently can destroy the design. Exact versus Monte Carlo enumeration changes resolution and computation, not the need for valid exchangeability. [Permutation tests](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html)

Define the family of claims before multiple comparisons. Holm-type procedures target family-wise error; BH-type procedures target false discovery rate under their dependence conditions. Correction cannot repair cherry-picked outcomes, invalid sampling, or repeated unplanned peeking. Correlated CV-fold scores should not be fed to an ordinary independent-samples t-test as if they came from independent experiments. [Multiple-testing methods](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html)
