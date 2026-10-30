# Maintainer evaluations

The deliverable is the 1ml plugin. This directory contains verification infrastructure, not another runtime service. Code/package tests live in `tests/`; agent evaluations assess decisions and deliverables separately.

## Layout

- `harness/`: reusable execution, storage, history and verification helpers.
- `skills/cases/`: fresh-agent behavioral tasks and fixture preparation.
- `skills/trials/<case>/<trial>/`: ignored local trials, with separate frozen materials, actor project and evaluator evidence.
- `static/`: ignored immutable shared plugin versions.
- `kaggle/<dataset>/`: ignored local datasets and results. Two legacy evaluator source modules are retained because synthetic unit tests import them.

Existing instruction-only cases remain under [tests/evals](../tests/evals/README.md). Their generated outputs are ignored. These are distinct from the end-to-end cases in [skills](skills/README.md).

## Evaluation contract

Prepare a fresh task and frozen plugin, record acceptance criteria before dispatch, and let the agent complete its work without parent interventions. Review only after it finishes. Freeze artifact hashes, inspect the actual notebook/plots/decisions, replay in a disposable copy, and preserve the original results. Fix the plugin and run a new trial when needed; do not repair a failing actor result and report it as autonomous success.

Separate scientific quality, installation/discovery, execution reliability, selective resource loading, resource limits, and infrastructure failure. A passing unit test, native skill call or automatic grader is not evidence of all these properties.

## Learner project layout

Current notebook, requirements and supporting modules belong at the dataset/project root. Current models, predictions and reports live in descriptive child folders. `runs/<revision>/` contains notebooks only. Keep immutable inputs and source/dependency versions once, outside notebook history; regenerate historical models. Historical replay must restore the matching companions and execute the verification appropriate to that revision.

The [notebook protocol](../references/notebook-protocol.md) defines the agent's delivery obligations. Parent-authored publication helpers are legacy maintainer utilities; fresh autonomous delivery trials require the agent to create this structure itself.

## Local prerequisites

Install [harness dependencies](harness/requirements.txt) in an evaluation environment. FCC tests additionally need an installed/configured FCC runtime. Dataset-backed cases need independently acquired authorized inputs; public source excludes those inputs, credentials, models and trial traces. Synthetic database/HTTP fixtures are created locally by their case preparation script.

Prefer accessible standalone datasets when competition joining is unnecessary. Do not bypass source permissions or licensing. No evaluation command implies authorization to submit predictions.

Local execution helpers are not an OS security sandbox. Keep credentials and sealed labels outside actor inputs, preserve failures, and distinguish agent self-repairs from reviewer assistance.
