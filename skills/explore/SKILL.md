---
name: explore
description: Investigate data structure, quality, relationships, or model errors with question-led exploratory analysis. Use when observations need explanation before deciding on collection, features, models, or scope; inferential claims belong to statistics.
---

# Explore to resolve a question

Identify the decision this analysis should inform and the evidence population it may inspect. Use [state](../../references/project-state.md) to reuse source/split definitions. Initial schema and integrity checks can precede splitting; adaptive feature/target/model exploration for prediction belongs to development data. Keep final evaluation reserved.

Read [question-led EDA](references/question-led-eda.md) for the relevant patterns and failure routes. Load a matching [task profile](../../references/tasks/index.md) when time, censoring, exposure, labels, or representation alter interpretation.

## Investigate

Inspect units, row/entity counts, ranges, missingness by source/time/group, category frequency, outcome support, duplicates/joins, and availability at decision time. For a runnable exploratory notebook, produce and inspect the figures needed to understand consequential distributions, missingness and relationships; printed summaries alone do not resolve visual questions. Choose relevant branches from the [visual evidence guide](references/question-led-eda.md#visual-evidence-and-decisions), rather than plotting every column. Compare distributions and error patterns by meaningful subgroups; record small support rather than interpreting unstable plots as facts.

Distinguish an observed association from a causal explanation. High skew alone does not imply a nonlinear model or a required transformation. A missingness percentage does not identify its mechanism. A visually separated cluster does not establish actionability. Inspect artifacts that could explain suspiciously good scores, including leakage and duplicated entities.

When considering correlation, covariance, skewness or kurtosis, follow [statistic selection](references/question-led-eda.md#choose-descriptive-statistics-for-the-decision). Use meaningful columns and report support; compute the statistic when it informs a decision, not merely to fill a checklist. Link observed structure to the feature-construction or no-change decision in prepare.

For model error analysis, use development predictions and actual costs to select representative ordinary and expensive errors. Preserve the denominator, failed predictions, and unlabeled cases. Generate specific hypotheses and test one plausible cause at a time. If analysis uses final-test outcomes to adapt a model, record that the test has become development evidence and request renewed evaluation.

## Record and route

Save reproducible calculations and rendered figures in the [notebook](../../references/notebook-protocol.md). Make the population/support, finding, relevant limit and resulting decision clear for each consequential analysis. Related figures can share one interpretation; labels, legends and a concise caption can supply context without a separate prose checklist. Explain what the evidence changes, including retaining the current approach. Verify that saved outputs actually contain the figures and that captions match the executed values. An import of a plotting library, a planned chart or an unfinished placeholder is not visual evidence. Separate measured facts, hypotheses, and unsupported claims.

- Source corruption, units, or ambiguous joins: return to [data](../data/SKILL.md).
- Invalid target/population or no useful action: return to [frame](../frame/SKILL.md).
- Statistical uncertainty, comparisons, or model-assumption inference: use [statistics](../statistics/SKILL.md).
- Candidate representation supported by evidence: use [prepare](../prepare/SKILL.md).
- Measured model failure or candidate comparison: use [train](../train/SKILL.md).
- Unsupported split or leaked observations: use [evaluation](../evaluation/SKILL.md) and invalidate affected results.

Complete when the investigation answers its question with limitations or identifies the exact missing evidence. An exhaustive gallery of plots is not a completion criterion.
