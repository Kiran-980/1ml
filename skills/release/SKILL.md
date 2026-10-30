---
name: release
description: Package a supported model or decision system and prepare or perform an authorized rollout. Use for serving contracts, artifact parity, resource checks, fallback, rollback, and monitoring ownership after intended-use evidence is available.
---

# Release a supported bundle

Identify the requested destination, exact fitted bundle, intended use, validation evidence, intervention evidence if needed, and release authority. Use [state](../../references/project-state.md) and [packaging/rollout](references/packaging-rollout.md). A notebook/report or scheduled batch may satisfy the action; do not create an API by default.

Package preprocessing, estimator, label mapping, calibrator, policy, schema, dependency environment, source/code lineage, expected inputs/outputs, and limitations. Include retrieval/index/prompt settings for applicable generative systems. Load only trusted serialized artifacts; pickle-like formats may execute code. Conversion or environment changes require parity evidence.

Define input units/freshness, prediction meaning, unsupported cases, error handling, and output consumers. Verify serialized-versus-training behavior, end-to-end latency/memory, cold start or batch duration as relevant, dependency failures, retry/idempotency, and actual fallback quality/capacity. A fallback must specify what the user receives and under what staleness/delay limits.

Prepare staged rollout or shadow checks where useful, explicit owner/alerts, rollback criteria, and a compatible previous bundle. Rollback cannot repair an upstream unit/schema error that breaks both models; define an independent fallback or halt behavior. Use [operate](../operate/SKILL.md) to establish monitoring and incident responsibilities.

## Gate and outcome

If quality or intended-use support is missing, return to [validate](../validate/SKILL.md); artifact/config mismatch goes to [train](../train/SKILL.md) or [prepare](../prepare/SKILL.md). A failed runtime boundary requires measured diagnosis, not weakening the evidence threshold. Deployment is conditional on requested use and authorization.

Check [capabilities](../../references/capabilities.md) before selecting a provider integration. This plugin supplies release guidance and local helpers, not a preconfigured cloud credential/deployment adapter. Inspect the actual platform and current primary documentation when needed. Installation, publication, account changes, and live traffic exposure stay within the user's authorized scope.

Save package identity, reproducible checks, rollout/rollback instructions, monitoring owner, and actual deployment outcome in the [notebook](../../references/notebook-protocol.md). Report a prepared package as prepared, a failed release as failed, and a completed deployment only from verified platform evidence. Pass the resulting system contract to operate.
