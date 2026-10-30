---
name: prepare
description: Construct preprocessing and features for specified model candidates and prediction-time inputs. Use for missingness, scaling, encoding, resampling, feature selection, or pipeline compatibility; fit learned operations only within the declared evaluation boundaries.
---

# Prepare candidate-compatible inputs

Establish source semantics, prediction-time availability, candidate requirements, and the [evaluation](../evaluation/SKILL.md) design. Read relevant [state](../../references/project-state.md). If the user asks only about a transformation, answer or investigate that question without running the full lifecycle.

For an explanation or design review without project artifacts, use the methodological references only. State and notebook protocols below apply when inspecting, creating, or updating project records; do not load them just to answer the question.

## Load the branch that matters

| Condition | Reference |
|---|---|
| Missingness, imputation, and preprocessing before/after splitting | [Missing data and timing](references/missingness.md) |
| Scaling versus normalization, categories/text, weights or resampling | [Representations](references/representations.md) |
| Feature availability, selection, output validity, transformation order, or whole-sample exceptions | [Features and checks](references/features-checks.md) |
| Target encoding/stacking/calibration/early stopping inside CV | [Inner validation](../evaluation/references/inner-validation.md) |

## Build and check

Apply fixed semantic corrections consistently when justified by external definitions. Fit learned imputers, vocabularies, scalers, selectors, resamplers, and other data-dependent operations within each permitted training fold; transform validation/test with the fitted operation. Sampling occurs only on training data. Internal cross-fitting must honor the outer time/group design.

Sharing a preprocessing specification across candidates does not permit fitting it before CV. For design-only requests, give a transformation specification rather than unverified API-shaped code. If implementing conditional row logic, preserve row alignment; `ColumnTransformer` selects columns, not population subsets. Compute missing indicators from the original missing mask, before imputation erases it.

Choose representations jointly with candidates: native missing/categorical support may remove a transformation; distance-based imputation needs meaningful scales; sparse/dense conversions can exceed memory; log/power/nonnegative methods impose domain constraints. Missingness fraction or skew alone is not a prescription. Preserve structural not-applicable/unknown semantics rather than filling them with a frequent value by default.

Create a reusable pipeline specification and test alignment, output schema/domain, unknown categories, allowed missing markers, expected failures, resource behavior, and inference parity. Unexpected infinity or NaN is a failure; intentional missing markers may be valid for the receiving estimator. Avoid target leakage from derived dates, global aggregates, target encoding, or features unavailable at decision time.

Before fitting candidates, execute one fit/transform smoke check on the exact input schema the full pipeline will receive at inference. Distinguish raw rows from already-engineered matrices; feed each transformation once and keep required columns until their consuming step. A learned fill value belongs in `fit`; a fixed semantic value must be described as fixed. Missingness counts alone do not identify a mechanism or prove structural absence.

## Completion and return

Record the chosen pipeline, rationale, feature provenance, fitting boundaries, and actual checks in the [notebook](../../references/notebook-protocol.md). A transformation is supported by the task and comparison evidence, not by a rule-table match alone.

For full predictive work, explicitly decide whether additional feature construction is useful using the [feature-engineering decision path](references/features-checks.md#decide-whether-feature-engineering-is-needed). Show source columns, definitions or a justified no-change, availability, and the actual evidence for retaining each representation. Distinguish a proposed feature from an independently demonstrated improvement.

Make the processing observable: show a bounded raw-to-processed example or feature-schema/shape summary, the learned-versus-fixed operations, and outcomes of applicable acceptance checks from [features and checks](references/features-checks.md). Reuse a permitted fitted transform or training-only smoke check; do not fit on final evaluation data to produce a demonstration. Pipeline code without observed output/handling checks is an implementation plan, not verified preparation.

Send the specification to [train](../train/SKILL.md), which fits it inside its evaluation loop. Return source/availability defects to [data](../data/SKILL.md), and infeasible splits to evaluation. A new model candidate may require a new representation; retain comparable evaluation conditions. Refitting that changes scores must follow [final fitting](../train/references/final-fitting.md). Invalidate affected fits and metrics when features or transforms change.
