---
name: statistics
description: Estimate means or effects and assess confidence intervals, CLT arguments, survey weights, clustered samples, statistical tests, or diagnostics. Use for descriptive and inferential questions as well as ML uncertainty; prediction holdouts are not mandatory for survey estimation.
---

# Match statistical evidence to the claim

For design-only questions, use the relevant methodology without project-state or notebook files. Verify a library's actual API before naming executable methods. Few clusters require a design-specific variance argument; a method is not valid merely because it is called a cluster bootstrap or robust standard error.

Establish the estimand, sampling/assignment mechanism, independent unit, population, missingness, and whether the question is exploratory or confirmatory. Read relevant [state](../../references/project-state.md); a descriptive whole-sample analysis does not need an artificial prediction holdout.

For inference, CLT, comparisons, dependence, intervals, or multiple testing, read [inference](references/inference.md). For residuals, collinearity, robust standard errors, stationarity, or interpreting diagnostic remedies, read [diagnostics](references/diagnostics.md). Load the relevant [task profile](../../references/tasks/index.md) when domain structure changes the method.

## Perform the appropriate calculation

Select the method from the design and estimand, not from whichever test produces significance. Distinguish paired from independent observations, repeated/clustered measurements, counts/proportions, continuous effects, and censored or temporal outcomes. Account for dependence and sampling weights where applicable. Missing assumptions are not satisfied because a library accepts the input.

Check the assumptions needed for the requested claim. CLT arguments concern sampling distributions under conditions; they do not make every feature normal or guarantee a small dependent sample is adequate. A normality-test result alone does not select linear versus nonlinear prediction. Robust standard errors address an uncertainty calculation, not omitted confounding or misspecified effects.

Report effect estimates, units, sample/event support, uncertainty method, practical magnitude, and assumptions. Keep exploratory selection and confirmatory analysis distinct. Ordinary post-selection p-values and repeated fixed-horizon significance checks do not retain their nominal interpretation automatically. Use a justified multiplicity/sequential design when relevant.

## End with the bounded claim

Persist code, actual results, diagnostics, limitations, and next action in the [notebook](../../references/notebook-protocol.md). Report inconclusive evidence when precision or identification is inadequate; do not treat failure to reject as equivalence or no effect.

Intervention design/assignment questions go to [experiment](../experiment/SKILL.md), with the [causal profile](../../references/tasks/causal.md) when observational identification is required. Predictive evaluation uncertainty goes to [evaluation](../evaluation/SKILL.md) or [validate](../validate/SKILL.md). Source failures return to [data](../data/SKILL.md). If data support no valid claim, specify the needed design/collection change rather than selecting a more permissive test.
