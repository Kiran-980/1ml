# Project outputs and verification

[1ml](../README.md) guides an agent's decisions. A notebook should follow the problem's questions and results, with explanations where they help the reader. The lifecycle does not require identical headings or Markdown around every cell.

## Delivered files

The agent chooses a descriptive notebook name from the task. A typical project looks like:

```text
shipment-delay/
  shipment-delay.ipynb       # current executed notebook
  requirements.txt
  README.md
  modeling.py               # when supporting modules are useful
  models/                   # current regenerable model
  predictions/              # or submissions/ for competitions
  reports/                  # metrics and verification evidence
  1ml/state.json             # workflow decisions
  runs/01-ingestion/
    shipment-delay.ipynb     # notebook-only history
```

Detailed coverage and run records can live in linked reports; consequential assumptions and limitations stay beside the findings they qualify. A statistical report, collection plan, deterministic solution or retained baseline may be the right result instead of a trained model.

Data may stay in its authorized database, URL, dataframe or local format. CSV export is not a prerequisite. Immutable inputs are shared; previous notebooks record source and dependency versions for reconstruction without historical model weights or duplicate environments. See the [notebook protocol](../references/notebook-protocol.md).

## Dependencies and execution

Python helpers require **Python 3.10+**. From a plugin checkout, install helper dependencies with:

```sh
python -m pip install -r requirements.txt
```

Modeling and notebook-execution dependencies are task-specific. The agent should record them in the learner project's requirements and provide a runnable installation cell. Paths, installation and verification must work from the documented project location. See [setup](../references/setup.md) and [capability boundaries](../references/capabilities.md).

## What verification establishes

Installation checks establish that skills and their references can be loaded. Mechanical tests check implementation behavior. Neither establishes that a model's scientific claim is correct or that an unattended agent will behave reliably.

The [scenario cases](../tests/scenarios/decision-paths.md), [behavioral evaluation guide](../tests/evals/README.md) and [observed results](../tests/evals/results-summary.md) record a separate layer of evidence, including failures. Local trials are not a guarantee of future performance or cross-host certification.

For development setup and test commands, see [CONTRIBUTING.md](../CONTRIBUTING.md). Generated experiments, datasets, weights and credentials are excluded from the plugin repository; the runtime does not depend on local research artifacts.
