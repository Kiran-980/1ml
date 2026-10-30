# metrics policy

## 2.3 Classification metrics follow the cost and output

| Situation | Candidate evaluation | Required companion checks |
|---|---|---|
| Equally costly exclusive decisions in the intended population | Accuracy, confusion matrix | Check per-class counts/errors and the deployment class mix. Imbalance does not invalidate accuracy, but accuracy alone can conceal unacceptable rare-class performance. |
| Missing positives is costly | Recall at a required precision or false-alert limit | Operational alert volume and uncertainty in rare positives |
| False alarms are costly | Precision at a required recall | Prevalence, missed events, review cost |
| Fixed review capacity | Precision/recall at k or budget; expected net value | Tie policy, capacity over time, workload, event deduplication |
| Need ranking across thresholds | ROC AUC and relevant operating region | Does not establish probability calibration or useful precision at rare prevalence |
| Rare positive retrieval | Precision-recall curve and average precision | Positive prevalence and candidate population |
| Need probabilities for decisions | Log loss or Brier score, reliability plots | Discrimination, calibration by relevant slices, sample support |
| Multiple classes/labels | Per-class metrics plus justified macro/micro/weighted aggregate | Rare class visibility, label support, thresholds and costs |

Average precision uses recall-weighted precision increments and differs from trapezoidal PR area. Report the exact implementation. Macro weights classes equally, weighted averages use class support, and micro aggregates individual label decisions. [Average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)

F1 trades precision and recall but ignores true negatives and does not encode an arbitrary business cost matrix. F-beta expresses a metric preference, not a universal conversion of money into a weight. Define the zero-division policy and report support where metrics are undefined. [F1 definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)


## 2.4 Regression metrics encode which quantity is valuable

| Needed estimate or cost | Candidate loss/metric | Consequence |
|---|---|---|
| Typical absolute error | MAE | Targets a conditional median; interpretable in outcome units |
| Strong penalty for large errors | MSE/RMSE | Squared loss targets conditional mean; inspect costly tails |
| Asymmetric shortage/overage | Quantile/pinball loss | Select quantile from the action's asymmetry |
| Nonnegative counts/rates | Appropriate count deviance and operational error | Model exposure, zero behavior, dispersion, output domain |
| Positive skewed amount | Appropriate positive-response model or carefully justified transformation | Evaluate on original business scale; retransformation changes estimands |
| Compare differently scaled series | Suitable scaled error against a meaningful baseline | Denominator can fail for constant/short series |
| Need uncertainty | Interval coverage plus width; quantile/distributional scoring | Wide useless intervals must not win from coverage alone |
| Multiple outputs | Per-output errors plus justified aggregate weights | Units and one poorly served output can be hidden by averaging |

Loss and estimand are linked; choosing a loss is more than changing a dashboard number. R-squared can be negative on held-out data and is not a percentage of predictions correct. [Metric and scoring foundations](https://scikit-learn.org/stable/modules/model_evaluation.html)

Pinball loss targets a chosen quantile. Under a simple inventory model with constant marginal underage cost Cu and overage cost Co, the optimal quantile is Cu/(Cu+Co); constraints, substitutions, lead times, and changing marginal costs require a fuller decision model. This equation is a decision-theoretic derivation, not a general inventory policy. [Pinball loss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_pinball_loss.html)

MAPE becomes unstable near zero and is undefined at zero mathematically; library safeguards can return enormous finite values. A zero-demand business does not become valid for MAPE merely because the function returns a number. [MAPE implementation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html)


## 2.5 Convert predictions into decisions

The default binary threshold is an implementation convention. Select a threshold using validation data and the operating objective; evaluating many thresholds on the test set is model selection. When using cross-validation, threshold selection must be contained in the training/selection procedure. [Threshold tuning](https://scikit-learn.org/stable/modules/classification_threshold.html)

For a calibrated probability p, fixed false-positive cost CFP, fixed false-negative cost CFN, and zero cost for correct decisions, comparing expected losses gives a positive decision when p > CFP/(CFP+CFN). This derivation assumes the costs and probability apply to the deployment population and the action does not alter the definition of the outcome being predicted. Capacity constraints, heterogeneous benefits, or intervention effects change the policy.

If only the top k cases can be reviewed, optimize that allocation and validate workload. If decisions have different costs per case, rank expected utility rather than raw risk where the estimates support it. If neither action is acceptable at low confidence, define an abstention/review route and measure coverage, residual error, review burden, and delay. Confidence is not evidence that an out-of-distribution case is safe.

Calibration compares predicted probabilities with observed frequencies. Calibrate using data independent of base-model fitting or a suitable cross-fitting procedure, with an untouched evaluation set afterward. Sigmoid and isotonic methods have different flexibility/data requirements. Brier and log loss jointly reflect more than calibration alone. Reweighting, resampling, and prevalence changes can alter probability interpretation. [Calibration guide](https://scikit-learn.org/stable/modules/calibration.html)


## 2.6 Resolve competing objectives explicitly

When accuracy, latency, cost, interpretability, fairness, and robustness disagree, first identify hard constraints, then compare the feasible alternatives. Report a tradeoff frontier or a small comparison table; do not invent weights to force one winner. A simpler model within practical equivalence may be preferable because it is cheaper to operate, but verify the equivalence margin and uncertainty rather than declaring scores tied by rounding.

Metric approval is a business/domain decision when it encodes harm, capacity, or cost. The agent can compute alternatives and expose tradeoffs; it cannot infer an organization's acceptable harm from a dataset. Revisit framing if no measurable proxy tracks the desired outcome. Proceed to split design only after the output, evaluation population, and consequential decision are sufficiently specified.


## 2.7 Aggregation and incomplete targets

Decide who or what receives equal weight. An error per transaction, average error per customer, and average error per site answer different questions when customers/sites have different volumes. For a daily review budget, evaluate each day's allocation before aggregating; taking the best 200 records over a whole month does not test a 200-per-day policy. For forecasts, state how horizons and series are weighted. Report both the primary operational aggregate and important disaggregated results.

An unweighted mean of fold scores gives equal weight to folds, not necessarily to observations. Pooling out-of-fold predictions can produce a different answer, particularly for non-additive metrics such as AUC/F1 and unequal folds. Choose the aggregation for the intended estimand in advance and preserve fold-level results. Repeated-CV or overlapping-origin predictions must not silently count the same case as independent new evidence. [Cross-validation prediction caveats](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_predict.html)

Keep a label-observation mask when only some labels/outputs are known. Score verified outcomes with explicit denominators and coverage; do not convert an unannotated multilabel class to a negative. If missingness is selective, the resulting score describes the observed subset unless an appropriate observation/sampling design supports a broader inference. Return to [collection](../../data/references/acquisition.md) or the [scarce-label route](../../../references/tasks/scarce-labels.md#few-labels-semi-supervised-and-active-learning) if that subset cannot support the business claim.

For undefined metrics, report the condition and support count. A single-class fold, no predicted positives, or a zero scale denominator needs a deliberate evaluation response. Keep model failures and abstentions in system-level reporting; excluding them from a model-only score does not make them disappear from business impact. The [split infeasibility routes](inner-validation.md#36-when-a-valid-split-is-not-feasible) explain what to do next.


## 2.8 Resolve target types that do not fit a default classifier

| Target situation | Concrete route | Decision boundary |
|---|---|---|
| Ordered labels with meaningful ordering but no equal distances | Compare a suitable ordered probability model with a multiclass baseline; evaluate order-sensitive business errors and probability quality | Integer labels alone do not justify ordinary least squares or equal-distance MAE. If distances are meaningful, a regression comparison may be reasonable; document the interpretation. |
| Multiple dependent outputs | Start with per-output baselines; compare joint models/chains only if dependence improves supported validation | Predictors available for one output must also be available when predicting another; training with true earlier outputs but serving with predicted ones creates a mismatch. |
| Partial multilabel annotation | Preserve unknown labels; obtain verified positives/negatives or use a method designed for the observation process | Ordinary complete-label accuracy/F1 is not justified by replacing unknowns with zero. |
| New target classes can appear | Define an unknown/review route, evaluate known-versus-unknown rejection separately, and collect/version labels for new classes | A fixed closed-set classifier cannot output an unseen class. Low maximum probability is a possible detection baseline, not a guarantee of detecting novelty. |
| Business wants several actions with asymmetric costs | Define a cost/utility matrix and choose the action minimizing conditional expected loss, subject to constraints | A binary threshold formula does not generalize unchanged to multiclass actions or interventions with causal effects. |

Ordered regression models provide probabilities over ordered categories; their particular link/shape assumptions still need checking. [Statsmodels ordinal example](https://www.statsmodels.org/stable/examples/notebooks/generated/ordinal_regression.html). Probability-based rejection has been studied as a baseline for misclassification/out-of-distribution detection, not a universal solution. [Hendrycks and Gimpel](https://arxiv.org/abs/1610.02136)

For any rejection/review policy, validate accepted-case errors together with rejection coverage, review capacity, and missed unknowns. If representative unknowns cannot be sampled, explicitly limit the novelty-detection claim and retain a fallback. New classes or target-ontology changes reopen [labels and evaluation](labels-splits.md), rather than being treated as mere unseen input categories.
