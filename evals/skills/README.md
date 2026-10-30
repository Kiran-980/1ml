# Fresh-agent behavior evaluations

Case source lives in `cases/<case>/`. Generated evidence belongs in ignored `trials/<case>/<trial-id>/`, separate from unit tests and delivered notebook history.

| Case | What it exercises |
|---|---|
| [Chart labels](cases/chart-labels/task.md) | Correct chart identity after filtering and nonconsecutive-ID sorting |
| [Autonomous delivery](cases/autonomous-delivery/task.md) | Complete root project, clean notebook replay and notebook-only historical reconstruction |
| [Database and URL](cases/database-url/task.md) | Read-only SQLite plus live HTTP JSON loading, joins, lifecycle analysis and delivery without input CSV exports |

These are maintainer scenarios, not automatic claims of correctness. Preparation may require local runtime configuration or previously acquired data. Generated materials and evaluations are not distributed.

Local Astra observations on 2026-10-27: the chart-label case passed; autonomous delivery trial 001 exposed an incorrect historical-verification command; trial 002 passed independent current and historical replay after the skill fix, with one disclosed startup-time budget violation. Detailed immutable evidence remains in the maintainer's local trials. There is no cross-host reliability certification.

On 2026-10-28, the database/URL trial passed independent direct-source replay, prediction/metric parity, current delivery and ingestion-history reconstruction. Actor results were not repaired. One interrupted sandbox attempt lacked elapsed-time evidence, so its resource-limit compliance remains unverified. The sources were synthetic SQLite and loopback HTTP JSON, not production authentication or every database vendor.

For each new trial, freeze inputs and plugin, start an empty actor project, predeclare gates, and dispatch a fresh agent. Do not inspect unfinished actor work or intervene. After completion, freeze hashes, review the notebook/code/figures, execute the documented workflow in a disposable copy, and compare source identities and predictions. Preserve unsuccessful trials. Never overwrite their outputs to create a pass.

Older instruction-level cases and their runner remain under [tests/evals](../../tests/evals/README.md). New trials use this directory; `runs/` inside an ML project is reserved for notebooks.
