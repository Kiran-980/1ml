---
name: lifecycle
description: Start or resume a machine-learning project, assess its current evidence, and coordinate the relevant 1ml skills. Use for broad lifecycle work or cross-stage changes; specific analyses can enter their owning skill directly.
---

# Coordinate the current question

Resolve Markdown links relative to this skill's directory. Shared `../../references/` files are under `<plugin-root>/references/`; preserve the parent-directory segments when reading them.

Use the user's requested outcome, existing evidence, and current constraints to select the next useful task. A working model, a statistical report, a collection plan, retaining a rule, and a justified no-go can all be correct endpoints. Do not equate completing the lifecycle with deploying a model.

## Enter and resume

Locate the learner project and inspect its notebook/state before asking for information already available. For project work, read [state and transition rules](../../references/project-state.md). For a narrow explanation, answer without creating state or running unrelated analysis. Read [setup](../../references/setup.md) only when helpers or environment checks are needed.

Read a compact state summary, then the specific evidence behind the current decision. Confirm artifacts still match the data, split, configuration, and intended claim. A completed label in state is not independent proof. Reconcile stale or interrupted work before relying on it; preserve user edits and original results.

Reuse instructions already read in the current context. Once the current question's inputs and execution route are known, save and run the smallest useful checkpoint before exploring later stages. Repeatedly rereading unchanged setup material is not additional evidence; identify a concrete missing capability or use the available executor's contract.

## Select an owner

Before authoring a stage's analysis or code, invoke/read its owning skill below. This router selects owners; it does not contain their methods. Record the relevant skill/reference paths with the resulting decision so later review can distinguish following the workflow from merely naming its stages.

| Immediate question | Invoke/read |
|---|---|
| Is this a useful/evaluable ML problem; what action or outcome? | [frame](../frame/SKILL.md) |
| Where is the data; can we collect/load/join it correctly? | [data](../data/SKILL.md) |
| What labels, metrics, groups/time boundaries, or validation roles? | [evaluation](../evaluation/SKILL.md) |
| What patterns or failures explain an observed problem? | [explore](../explore/SKILL.md) |
| What statistical design, effect, interval, or assumption applies? | [statistics](../statistics/SKILL.md) |
| How should this candidate represent inputs? | [prepare](../prepare/SKILL.md) |
| Which baseline/model/search/refit procedure earns support? | [train](../train/SKILL.md) |
| Does the frozen system support its intended use? | [validate](../validate/SKILL.md) |
| Does an intervention change outcomes? | [experiment](../experiment/SKILL.md) |
| How can this supported candidate be packaged and rolled out? | [release](../release/SKILL.md) |
| What caused this alert; should we repair, retrain, or retire? | [operate](../operate/SKILL.md) |

When specialized task conditions appear, use the [task-profile index](../../references/tasks/index.md) immediately. Forecasting, censoring, or causal identification can change framing and label design before any model is selected. Check [capability boundaries](../../references/capabilities.md) before promising execution of a specialist or provider integration.

## Transition without loading everything

Invoke the selected `1ml:<name>` skill when available, or read its linked body and follow it in the current agent. Pass the question, relevant evidence paths, declared prerequisites, unresolved choices, and allowed scope. Do not read all linked skill bodies or task profiles upfront. Skills remain separate entrypoints; the user may invoke them directly.

After the task, record its result and affected invalidations, then decide whether another skill is necessary for the original request. Revisit a failed task only with new evidence, a changed input, or a justified diagnostic. If a prerequisite remains unavailable, name it and give the next useful action; do not cycle through skills to manufacture progress.

Continue authorized reversible analysis. Ask only for consequential choices that evidence cannot establish, or additional authorization for actions outside the request. For runnable notebook work, read the [notebook protocol](../../references/notebook-protocol.md) before the first code plan and write findings incrementally. Before finishing, reconcile the user's requested deliverables with executed evidence and the relevant owners' completion criteria; resolve missing items or report them explicitly. Finish with the supported result, evidence, limits, and any remaining blocker.

For notebook deliverables, perform the protocol's [reader-facing completion review](../../references/notebook-protocol.md#review-before-calling-the-notebook-complete) before handing back the result. Each owning skill should leave its consequential reasoning beside the evidence as it works; do not defer lifecycle explanations to a user-requested repair or treat a successful executor response as the whole completion check.

For an end-to-end request, maintain the protocol's lifecycle coverage record from framing through the supported endpoint in project state, a linked report or a useful appendix. Route omitted applicable work to its owner before finishing. The agent chooses analyses and visualizations from the data and claim; the user should not have to enumerate missing checks. Coverage means evidenced decisions and executed work, not merely visiting skills or naming stages. Follow the protocol's [reader-facing narrative](../../references/notebook-protocol.md#reader-facing-narrative) guidance: skill transitions do not require new notebook headings or repeated handoff summaries.
