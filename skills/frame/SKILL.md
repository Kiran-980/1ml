---
name: frame
description: Decide whether ML is useful or whether a rule, lookup table, statistical analysis, or data collection fits better. Use for ML feasibility reviews and questions about business actions, population, targets, alternatives, data sufficiency, or success criteria.
---

# Frame an evaluable decision

For a design-only question, read the relevant methodology without project-state or notebook files. Resolve linked paths relative to this skill directory, including `../` segments; do not invent filenames. When judging whether ML is worthwhile, read feasibility before deciding. A deterministic design still needs contract/version tests; do not promise zero errors or measured latency without evidence, or disguise a lookup as ML.

Inspect the existing project before interviewing the user. For ongoing work, read the relevant [project state](../../references/project-state.md); reuse confirmed choices unless new evidence invalidates them. Read [feasibility](references/feasibility.md) when assessing alternatives, data sufficiency, or whether ML belongs in the solution.

1. Identify the action/decision owner, affected population, observation unit, decision time, available inputs, outcome horizon, present baseline, and costs or capacity constraints. Distinguish descriptive, inferential, predictive, and intervention-effect claims. A label guessed from a column name remains a hypothesis.
2. Inspect enough available data to determine whether the proposed observation/label process is plausible. Ask [data](../data/SKILL.md) for bounded acquisition/inspection when needed; a project without data may still produce a useful acquisition plan.
3. Compare ML against rules, lookup/search, ordinary analysis, optimization, human review, and existing products using the action and constraints. Count independent entities/events and relevant coverage; neither a universal minimum row count nor synthetic duplication establishes sufficiency.
4. For future values, censoring, ranking, causal effects, unlabeled structure, media, or sequential feedback, load the matching [task profile](../../references/tasks/index.md) before confirming the target. For ordinary predictive work, consult [task contracts](../evaluation/references/task-contract.md) to distinguish output and action.
5. Write the supported problem contract and unresolved assumptions. Explain consequential tradeoffs in the user's terms. Choose reasonable reversible defaults when evidence supports them; the acceptable cost of a harmful decision is a domain choice, not a model parameter to guess.

## Result and next path

Completion requires an explicit decision question, population/unit/timing, baseline, constraints, evidence limits, and one justified route. Save the reasoning with source/artifact references in the [notebook](../../references/notebook-protocol.md).

- Evaluable predictive question: send the contract to [evaluation](../evaluation/SKILL.md), with missing data semantics assigned to data.
- Inadequate or biased observations: produce a collection plan with source, sampling/annotation need, acceptance evidence, and re-entry condition; record `collect_data`.
- Intervention benefit: send to [experiment](../experiment/SKILL.md), not ordinary risk prediction by default.
- Descriptive/inferential question: send to [statistics](../statistics/SKILL.md) or [explore](../explore/SKILL.md) without inventing a supervised target.
- Deterministic solution or no worthwhile decision: record `no_go` for ML or `retain_baseline`, and deliver the appropriate alternative within scope. Completion of this analysis does not authorize downstream training.

Changed population, action, target, or horizon invalidates affected metrics, labels, splits, fits, policies, and claims. Record those dependencies explicitly before continuing.
