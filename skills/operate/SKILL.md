---
name: operate
description: Diagnose production ML incidents, alert spikes, schema or unit changes, delayed labels, drift, and retraining requests. Choose evidence-supported source repair, recalibration, collection, retraining, rollback, or retirement.
---

# Diagnose the operating system

For a recommendation without project artifacts, read monitoring methodology only; state/notebook protocols apply when handling actual records. Resolve links relative to this directory, preserving `../`. Separate proposed actions and expected recovery from actions performed and recovery measured.

Start with the incident or monitoring question, current bundle/version, source contracts, observation window, and actual failing evidence. Read [monitoring and recovery](references/monitoring-recovery.md) and relevant [state](../../references/project-state.md). Incident diagnosis can enter directly without completing a new training cycle.

Separate service errors, source integrity, train/serve mismatch, input drift, prediction drift, outcome prevalence, concept/relationship changes, predictive performance, and business/human outcomes. An input drift test alone cannot prove degraded quality or concept drift. Unchanged histograms do not prove continued performance.

Reproduce the actual failing boundary with bounded redacted evidence. Check recent schema/unit/source/config changes, latency, missing fields, staleness, event ordering and queue behavior before retraining. Compare mature comparable cohorts; account for label delay, changing review/selection policies, and unsupported populations. Monitoring thresholds need relevant windows, support, practical magnitude and an owner, not only a p-value.

Repair a units mismatch at the source/feature contract and verify replay/parity. Do not absorb a feature scaling bug with output calibration or a decision threshold: the model may respond nonlinearly. Rolling back model weights helps only if it restores a compatible input contract. Preserve incident records and label maturity rather than discarding a whole day or inventing monetary cutoffs.

## Choose the measured response

- Broken source, units, joins or label process: use [data](../data/SKILL.md) and source repair/fallback. Training on the broken source is not a cure.
- Pipeline or serving mismatch: use [prepare](../prepare/SKILL.md) or [release](../release/SKILL.md) with replay/parity evidence.
- Probability/policy deterioration: inspect calibration, prevalence, cost/capacity and selection; use [evaluation](../evaluation/SKILL.md) and [train](../train/SKILL.md) only for affected work.
- Supported need for retraining: collect/version evidence, compare a candidate, then pass through [validate](../validate/SKILL.md) and release. A schedule or alert does not waive gates.
- Business value disappears, inputs cease to be reliable, or a simpler solution wins: use [frame](../frame/SKILL.md), identify consumers/fallback, and plan retirement.

Streaming inference is not necessarily online training. For explicit incremental updates, evaluate predictions before learning from corresponding outcomes, honor delay, and preserve model/update lineage. New data and revised labels must not silently move old test records into training; document advancing evaluation windows.

Record diagnosis, observed consequences, action, remaining uncertainty, affected artifacts, and recovery evidence in the [notebook](../../references/notebook-protocol.md). Perform operational mutations only within actual authorization. A stopped output or retained baseline can be the correct endpoint. [Capability boundaries](../../references/capabilities.md) apply to provider integrations and unsupported specialist methods.
