# Project state and transitions

Use this protocol for project work across skills. A short conceptual answer need not create a notebook or state. Installed plugin resources are read-only; learner artifacts belong to the selected learner project, not the plugin cache.

## Enter

Use existing `1ml/state.json` and the notebook path it records. Initialize only a genuinely new project; initialization rejects an existing state. State v1 is read as v2 with all historical records preserved; prior non-pending evidence becomes stale until checked. The first save preserves `state.v1.json`. No silent reset or second `.1ml/` store.

When an execution tool explicitly initializes state and renders saved plans, use that contract: choose the notebook path, write its required manifest and first runnable plan, then call the executor. Manual CLI initialization and reading helper implementations are unnecessary in this branch. Record observed results after the tool returns; delegated initialization is not a reason to delay the first checkpoint or claim a completed stage.

Resolve the plugin root from the invoked skill's installed location. From a skill at `skills/<name>/SKILL.md`, helpers are at `../../tools/`. CLI examples use `<plugin>` and `<project>` as paths to substitute, not literal shell variables. Quote paths as single arguments; use the actual shell's syntax. See [setup](setup.md).

```text
python <plugin>/tools/state.py init --project <project> --name <task-name> --notebook <chosen-notebook-path> --goal "current user question"
python <plugin>/tools/state.py show --project <project> --summary
python <plugin>/tools/state.py configure --project <project> --stage train --depends-on evaluation prepare
python <plugin>/tools/state.py next --project <project> --stage train
python <plugin>/tools/state.py set-stage --project <project> --stage data --status complete --outcome supported --conclusion "Source manifest and profile verified: 1ml/artifacts/source-v1.json"
python <plugin>/tools/state.py invalidate --project <project> --stage evaluation --reason "Split changed to unseen sites"
```

## Evidence, completion, and dependency meaning

For a new project, choose the notebook path using the [notebook protocol](notebook-protocol.md) before initialization and pass it explicitly. A helper's fallback filename is not a task naming decision.

Declare only prerequisites actually required for this operation. `configure` replaces that task's dependency list and rejects cycles. Configure before completion. A common predictive route is evaluation → prepare → train → validate → release, but collecting data, descriptive statistics, or incident diagnosis can enter independently. Candidate selection can precede representation construction; avoid circular prepare/train dependencies by recording the candidate specification before requiring a fitted pipeline.

Statuses: `pending`, `running`, `complete`, `blocked`, `failed`, `stale`, `not_applicable`. Completion requires fresh findings; blocked/failed/stale/not-applicable requires a reason. Outcomes: `supported`, `no_go`, `inconclusive`, `collect_data`, `retain_baseline`, `needs_research`. A completed no-go does not satisfy a downstream training prerequisite. A justified not-applicable dependency may be satisfied; never use it to bypass a genuinely required design.

Use conclusions/decisions to reference measured artifacts with their source population, version, config, evidence, and limitations. The helper checks structural dependencies and revision consistency; it cannot verify the scientific truth of a sentence. The owning skill must inspect evidence and actual outputs. Rendering cells does not execute them or complete a task.

Changing a finished task invalidates declared dependents transitively and preserves historical snapshots. Granularity is currently task-level: record precise affected artifact IDs/versions in decisions, then conservatively invalidate the task that owns them. A cost-only change need not refit an estimator; revalidate affected policy evidence explicitly. Avoid representing reusable estimator fitting and a changed policy as indistinguishable evidence.

`next --stage` reports a missing declared prerequisite or the task itself; it never invents a universal next stage. A completed no-go/collection outcome ends the current attempt unless new evidence changes it. Ask for a missing consequential choice; use tools for observable facts. Do not rerun identical failed attempts without a new diagnostic purpose.

## Persistence and resumption

State saves use atomic replacement, a writer lock, and revision checks. Reload and reconcile on a stale revision. A leftover lock after a crash is a recovery signal: verify no writer is active, inspect files, then remove only the confirmed stale lock. Do not delete it automatically while another process may be writing. Single-writer project use is the supported workflow.

Save notebook/artifacts, verify them, record the results, then mark evidence complete. [Notebook replay](notebook-protocol.md) reconciles a successful cell write followed by a failed state save. On resume compare source/extract identity, config, environment and artifact existence; mark stale rather than trusting a completion flag. Keep raw rows, credentials and large logs out of state. Prefer the summary first, followed by a targeted task record/artifact read.
