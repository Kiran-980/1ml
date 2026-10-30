# task contract

## 2.1 Translate the action into a prediction contract

Complete this sentence with project evidence: **For this population, at this decision time, using these available inputs, estimate this output over this horizon so this actor can take this action under these constraints.**

For example, predicting which subscribers will cancel in 30 days is different from estimating which subscribers a support call will retain. The first estimates risk; the second estimates an intervention effect. If the team can call 500 people a week, evaluating every possible classification threshold equally misses the operational decision. Historical cancellation labels may be affected by the previous calling policy.

Resolve target meaning with domain evidence, not dtype inference. Integers may represent classes, counts, ordinal ratings, or identifiers. A numeric-looking postcode is not a continuous quantity. Multiple labels can coexist even when a single CSV cell contains them.

| Required output | Task route | Questions that change the route |
|---|---|---|
| One of two outcomes | Binary classification | Need a class, probability, ranking, or action? When is the outcome mature? |
| One of several exclusive outcomes | Multiclass classification | Are unseen classes possible? Are mistakes equally costly? |
| Several simultaneous outcomes | Multilabel classification | Separate thresholds? Missing annotations or true negatives? Dependencies between labels? |
| Ordered category | Ordinal modeling or justified ordered loss | Are adjacent errors less costly? Are distances between categories meaningful? |
| Continuous amount | Regression | Need mean, median, quantile, interval, or full distribution? |
| Nonnegative event count/rate | Count/rate modeling | Exposure duration? Excess zeros? Dispersion? |
| Future sequence | Forecasting | Horizon, origin, seasonality, known future covariates, known/new series? |
| Time until an event | Survival analysis | Censoring, time origin, competing events, recurrent events? |
| Ordered candidates for a query/user | Ranking/recommendation | Candidate retrieval, cutoff, feedback bias, cold start? |
| Useful groups without target labels | Clustering | What similarity and subsequent action make a group useful? |
| Unusual events | Anomaly/novelty detection | Clean reference data? Labels? Review capacity? |
| Effect of changing an action | Causal inference/uplift | Randomization or defensible identification and overlap? |
| Generated answer/content | Generative system, possibly retrieval | Evidence, factuality, permission, abstention, human rubric? |
| Actions with sequential consequences | Control/RL | Reward, dynamics, safe exploration, simulator or logged action coverage? |

Multiclass, multilabel, and multioutput are distinct target structures; wrappers and native estimator support differ. Preserve that distinction in label storage and scoring. [Scikit-learn target structures](https://scikit-learn.org/stable/modules/multiclass.html). Specialized routes continue in [chapter 7](../../../references/tasks/index.md).


## 2.2 Separate four objectives

**Training loss** guides fitting. **Selection metric** chooses candidates. **Business outcome** measures actual value after actions. **Guardrails** constrain unacceptable behavior. They can differ, but record why: logistic loss can train a ranker selected on recall among the 500 reviewed cases, while an experiment measures prevented losses and a latency budget constrains serving.

Specify direction, units, positive class, averaging, denominators, missing-label handling, evaluation population, sample weights, threshold/cutoff, uncertainty method, baseline, and minimum practically useful gain. Freeze this before broad search. A metric without its population and aggregation is not a reproducible objective.
