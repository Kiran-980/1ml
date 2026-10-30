# causal

## Causal effects and uplift

**Documented:** Causal analysis needs a causal model/assumptions, identification, estimation, and refutation/sensitivity checks. Choosing a powerful estimator alone does not identify an effect. [Original DoWhy paper](https://arxiv.org/abs/2011.04216)

**Decision synthesis:** Route 'what happens if we intervene?' here; predicting who churns does not identify whom an offer will help. Define treatment, comparator, outcome, population, horizon, and estimand (ATE, ATT, conditional effect, or policy value). Prefer a valid randomized design where feasible. For observational data, document identification assumptions, pre-treatment confounders, overlap, selection mechanisms, and possible interference. Do not adjust blindly for post-treatment variables. If identification is unsupported, stop causal claims and return to data/design collection or label the result associative.

**Documented:** Double machine learning estimates treatment effects under observed-confounder and structural assumptions, using predictive nuisance models and cross-fitting. Different final-stage estimators impose different effect-model assumptions. [EconML DML](https://www.pywhy.org/EconML/spec/estimation/dml.html)

**Decision synthesis:** Use held-out policy evaluation or an appropriate causal validation design, uncertainty intervals, overlap diagnostics, and sensitivity analysis. Treatment assignment is a legitimate input to a specified causal estimator; distinguish it from post-outcome information and fit nuisance models/cross-fitting within the causal design. Ordinary outcome-prediction accuracy does not establish a treatment effect. Refutation tests can expose problems but cannot prove absence of unmeasured confounding. Escalate instrumental variables, discontinuities, longitudinal treatment, and interference to a method-specific design rather than routing them automatically to a generic regressor.
