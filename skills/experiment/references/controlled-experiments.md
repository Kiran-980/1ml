# controlled experiments

## 8.4 Does this project need an A/B test?

An A/B test compares interventions under randomized assignment. It is not a prerequisite attached to a specific algorithm. Use one when the question is whether changing the deployed policy/product improves an observable outcome and a feasible, appropriate randomization is available. Offline accuracy does not demonstrate business impact because actions, users, and feedback can change the outcome. [Controlled experiments: original practical guide](https://link.springer.com/article/10.1007/s10618-008-0114-1)

| Question | Appropriate evidence route |
|---|---|
| Does the implementation compute valid predictions? | Software/data validation and replay |
| Does the predictive model generalize? | Independent offline evaluation matched to deployment |
| Does changing the user-facing decision improve outcomes? | Randomized controlled experiment where feasible |
| Is randomization impossible or inappropriate? | Defensible causal/observational design with explicit limits; see [causal route](../../../references/tasks/causal.md) |
| Does the service remain reliable under load? | Load/resilience tests, shadow/canary monitoring |
| Are two predictive models practically equivalent? | Appropriate paired evaluation/interval with prespecified margin; this alone is not an online intervention test |

Shadow traffic tests execution without exposing users to the new decisions. Canary rollout limits operational exposure. Neither automatically supplies a valid causal experiment.


## 8.5 Experiment design before exposure

Define treatment and control as complete policies, eligibility, assignment unit, exposure, outcome window, primary estimand/metric, guardrails, minimum detectable/practically useful effect, alpha/power or other inferential framework, sample-size/duration assumptions, and stop/rollback rules. Plan logging and analysis before starting.

Choose an assignment unit that addresses contamination: repeated visits from a user generally need consistent assignment; household/site/network effects may require clusters or a different design. Analyze at the unit implied by randomization/dependence. Ratio metrics and variable cluster sizes require appropriate variance calculations; page-view count is not automatically independent sample size.

Estimate power from a defensible baseline rate/variance and effect size, allowing for clustering, attrition, outcome delay, and multiplicity. If traffic cannot support the decision, revise the design, run a smaller learning pilot with appropriately limited claims, or choose another evidence route. An underpowered result is not proof of no impact. A/A tests can audit assignment and measurement but cannot prove every future experiment valid.

During analysis, preserve assignment-based comparisons when that is the estimand; filtering on post-treatment engagement can induce bias. Distinguish assignment, exposure, compliance, and missing outcomes. Identify novelty/carryover/seasonal effects and follow-up needs without declaring arbitrary fixed durations universal.


## 8.6 Trustworthiness and stopping

Check observed versus expected assignment/exposure counts using an appropriate sample-ratio-mismatch diagnostic. A meaningful mismatch may indicate assignment, logging, joining, filtering, or exposure failures. Diagnose before relying on effect estimates; passing this check is necessary evidence about one failure mode, not proof of all validity. [Original SRM research](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)

For a fixed-horizon design, follow the planned analysis horizon. If continuous efficacy monitoring/stopping is needed, choose a valid sequential approach in advance. Repeatedly inspecting ordinary fixed-sample p-values and stopping at significance invalidates nominal error rates. Monitoring urgent safety/reliability guardrails remains appropriate; record early stops and their implications for inference. [Always Valid Inference](https://pubsonline.informs.org/doi/10.1287/opre.2021.2135)

Report effect estimates, uncertainty, practical magnitude, guardrails, exclusions, and prespecified versus exploratory analyses. For multiple metrics/variants, apply the chosen multiplicity plan. If guardrails fail, stop/revert as designed and investigate. If evidence is inconclusive, keep that conclusion and identify the missing precision or design evidence. Avoid declaring a winner merely because one metric improves while an important cost is omitted.
