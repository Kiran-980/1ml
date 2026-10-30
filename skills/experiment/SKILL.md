---
name: experiment
description: Design or analyze randomized intervention experiments and assess when causal alternatives are needed. Use for A/B tests, power, assignment, outcome windows, stopping, effect estimates, or experiment-integrity questions, not ordinary algorithm validation.
---

# Establish intervention evidence

An A/B test is evidence about an intervention, not a prerequisite of a particular ML algorithm. Define treatment/control as complete policies, the population, action, target effect, outcome window, costs, and harms. Read [controlled experiments](references/controlled-experiments.md) and [state](../../references/project-state.md). For observational identification, confounding, overlap, or uplift, read the [causal profile](../../references/tasks/causal.md).

## Design before exposure

Choose eligibility, assignment unit, exposure logging, primary estimand/metric, guardrails, practical effect, alpha/power or other inferential framework, duration, and stop/rollback policy. Handle repeated users, clustered assignment, contamination/interference, variable cluster sizes, and delayed outcomes. Use defensible baseline rates/variance for power. If traffic or assignment cannot support the decision, revise the design or report a bounded pilot/inconclusive route.

Verify numerical power, MDE, and sample-size claims under explicit tail, effect, margin, and variance assumptions; reconcile numbers across prose and tables. If calculation tools are unavailable, give the qualitative conclusion and calculation plan instead of invented precision. Low power does not make non-significance certain. Noninferiority is a different claim with a justified margin, not automatically a small-sample workaround.

Specify analysis and multiplicity before observing results. Fixed-horizon tests do not support unplanned efficacy stopping at the first significant p-value; use an appropriate sequential method if continuous decisions are required. Urgent harm/reliability monitoring remains appropriate. Do not prescribe every test or a universal duration.

## Analyze trustworthy observations

Inspect assignment/exposure counts, sample-ratio mismatch, joins, attrition, missing outcomes, carryover, and logging changes. A compromised experiment needs diagnosis, not simply more samples. Preserve assignment-based comparisons when that is the estimand; post-treatment engagement filters may bias effects.

Use [statistics](../statistics/SKILL.md) for design-appropriate variance/interval calculations. Report effect size, uncertainty, practical magnitude, guardrails, exclusions, and prespecified versus exploratory analyses. Non-significance does not establish equivalence. Offline model quality, shadow traffic, and canary rollout alone do not establish causal improvement.

## Output and scope

Deliver a design, an analysis with verified outputs, or a precise missing-evidence plan in the [notebook](../../references/notebook-protocol.md). Return logging/data failures to [data](../data/SKILL.md), proxy/action problems to [frame](../frame/SKILL.md), and supported impact evidence to [validate](../validate/SKILL.md) or [release](../release/SKILL.md).

Designing an experiment does not authorize exposing users, contacting participants, or altering a live policy. Prepare the concrete design and checks first; perform external actions only within the user's actual authorization and supported environment. Unsupported causal identification remains a limitation, not a reason to substitute a predictive score.
