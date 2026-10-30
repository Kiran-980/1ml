# diagnostics

## 4.6 Model assumptions require model-specific checks

| Model or intended claim | Relevant checks | Response to concern |
|---|---|---|
| Linear regression prediction | Functional form, residual patterns, leverage, extrapolation, conditioning | Transform/expand features, regularize, robust model, nonlinear comparison |
| Classical coefficient intervals | Error variance/dependence, design/exogeneity assumptions, model specification | Robust/cluster-aware inference where justified, redesign, or limit claims |
| Logistic regression | Log-odds functional form, separation, conditioning, calibration | Regularization, nonlinear terms, more outcomes, calibration comparison |
| Count model | Exposure, link/domain, dispersion, structural zeros | Rate model/offset, different count family, hurdle/mixture design with evidence |
| Distance methods | Meaningful metric, feature scales, dimension, density | Change representation/metric or select another family |
| Gaussian generative model | Class-conditional/covariance structure appropriate to variant | Shrinkage/regularization or alternative family |
| Forecast | Residual autocorrelation, horizon errors, structural change, future inputs | Improve temporal model/features or revise deployment horizon |
| Survival | Censoring assumptions, time support, proportional hazards if used | Flexible/time-varying alternative or specialized analysis |

Residual plots against fitted values, features, time, and groups help distinguish functional-form errors, changing variance, and dependence. A high R-squared alone is insufficient evidence of fit. [NIST model validation](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm)

A normality test should address an actual assumption. Small samples may miss departures; large samples may reject inconsequential ones. SciPy notes that Shapiro-Wilk p-values may be inaccurate above 5,000 observations. Use graphical diagnostics and consequence-based sensitivity checks rather than an automatic 'reject normality, switch algorithm' rule. [Shapiro-Wilk](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html)


## 4.7 What leaves this stage

### Do the diagnostic result and proposed remedy answer the same question?

If variance/dependence assumptions fail, first identify what is affected: point prediction, coefficient uncertainty, or the causal interpretation. Robust standard errors can change uncertainty estimates without repairing a misspecified mean, leaked feature, or confounded causal claim. A different loss or model addresses a different problem. Document the remedy and recheck the affected claim instead of restarting every test.

Collinearity can make coefficients unstable even when predictions remain useful. Use domain meaning, regularization, stability, feature cost, and validation to decide whether to remove or combine inputs. A VIF/correlation cutoff is not a universal rule; removing a confounder to improve conditioning can damage a causal analysis. High-dimensional settings may not support ordinary unregularized coefficient inference at all.

Feature screening, model selection, and repeated hypothesis search change the inference problem. Ordinary p-values from a model fitted after selecting variables on the same outcomes do not automatically retain their nominal interpretation. If inference is the goal, use a prespecified design, an appropriate independent confirmation/sample-splitting approach, or a justified selective-inference method. If prediction is the goal, use predictive validation and avoid dressing selected coefficients as confirmatory discoveries. [Forecasting regression discussion of predictor selection and inference](https://otexts.com/fpp3/regression.html)

For time-series diagnostics, stationarity tests belong to the [specific forecasting branch](../../../references/tasks/forecasting.md#forecasting-and-time-series), not to every dataset. A failed test should change a justified model/design decision; it is not a mandatory reason to transform all columns.

Save the evidence needed to connect the observation and its population/split to the interpretation, uncertainty and concrete consequence. Use the notebook's existing figures and discussion rather than duplicating them in a fixed report template. Some observations require collection repair, some nominate a transformation, some nominate competing models, and some need no action. Maintain exploratory and confirmatory claims separately. Carry unresolved assumptions into evaluation and release criteria; do not silently turn them into facts.

Online A/B design is covered in [controlled experiments](../../experiment/references/controlled-experiments.md). It evaluates an intervention/system, whereas the checks here evaluate data, statistical claims, and model assumptions. Neither is a universal prerequisite list for every algorithm.
