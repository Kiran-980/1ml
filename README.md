# 1ml — Machine learning skills for AI coding agents

**Machine learning skills for classification, regression, time series forecasting, clustering and reproducible Jupyter notebooks.**

Use 1ml with Codex, Claude Code and other coding agents to choose sound baselines, prevent data leakage and turn model results into readable notebooks.

1ml helps a coding agent turn a business question and available data into a justified analysis, reproducible notebook, and tested model when ML is appropriate. A collection plan, statistical report, deterministic solution, or retained baseline can also be the right result.

Twelve connected skills cover the classical ML lifecycle, from exploratory data analysis and feature engineering to model evaluation and monitoring. Decisions follow the data and intended claim; every dataset does not need the same checklist. Generative AI workflows are outside the current focus.

## Classification, regression and time series workflows

| Machine learning task | What 1ml helps the agent decide |
| --- | --- |
| **Classification** | Binary or multiclass labels, class imbalance, grouped or stratified validation, precision/recall and probability calibration |
| **Regression** | Numeric targets, simple baselines, MAE/RMSE, target transformations and residual analysis |
| **Time series forecasting** | Forecast horizon, chronological backtesting, seasonal baselines and features available at prediction time |
| **Clustering** | Scaling and distance choices, cluster stability and whether the groups answer a useful question |
| **Exploratory data analysis** | Missing values, distributions, relationships, outliers and useful charts |
| **Model evaluation** | Data leakage, cross-validation, held-out tests, error analysis and reproducibility |

See [machine learning use cases and example prompts](docs/machine-learning-skills.md) for classification, regression, time series and unsupervised learning projects. 1ml guides the coding agent's analysis; the agent writes and runs the project code in your chosen environment.

## Start here

Claude Code:

```text
/plugin marketplace add Kiran-980/1ml#main
/plugin install 1ml@1ml
/1ml:lifecycle
```

For a local checkout: `claude --plugin-dir /absolute/path/to/1ml`.

Install separately in each agent you use. This repository is public; cloning it does not require repository access credentials. The [installation guide](docs/installation.md) includes local alternatives, updates and verification.

[Automatic updates](docs/installation.md#automatic-updates) use the host's plugin manager: Codex refreshes Git marketplaces at startup; in Claude Code, enable auto-update for the `1ml` marketplace once.

| Agent | Install / configure |
|---|---|
| [Codex](docs/installation.md#codex) | `codex plugin marketplace add Kiran-980/1ml --ref main`, then `codex plugin add 1ml@1ml` |
| [Claude Code](docs/installation.md#claude-code) | Commands above, or the equivalent terminal CLI |
| [Gemini CLI](docs/installation.md#gemini-cli) | `gemini extensions install https://github.com/Kiran-980/1ml --ref main` |
| [Pi](docs/installation.md#pi) | `pi install git:github.com/Kiran-980/1ml@main` |
| [OpenCode](docs/installation.md#opencode) | Clone and add the absolute `skills/` path to OpenCode configuration |
| [Hermes](docs/installation.md#hermes) | Clone and add the absolute `skills/` path under `skills.external_dirs` |

Native installation/discovery is verified in **Codex and Claude: all 12 skills and 194 local reference links pass**. The other agents have documented installation routes, not end-to-end certification. All routes share the same skill source; see the [verification record](docs/installation.md#verified-installation).

Example request:

> Use 1ml to understand this dataset and decide whether ML is useful. Load it from the supplied database or URL, choose the learning task, metric and split, and compare justified baselines and models. Produce an executed notebook with concise decisions, relevant EDA, requirements, model and test results. Do not deploy or submit anything.

## Connected, independently usable skills

| Skill | Decisions it owns |
|---|---|
| [lifecycle](skills/lifecycle/SKILL.md) | Start/resume, select the next owner, reconcile evidence and deliverables |
| [frame](skills/frame/SKILL.md) | Business action, learning family, feasibility, no-ML alternatives |
| [data](skills/data/SKILL.md) | Collection, loading, joins, labels, lineage and quality |
| [evaluation](skills/evaluation/SKILL.md) | Metrics, baselines, time/group boundaries and test roles |
| [explore](skills/explore/SKILL.md) | EDA, useful plots, anomalies and investigations |
| [statistics](skills/statistics/SKILL.md) | Estimands, assumptions, uncertainty and statistical tests |
| [prepare](skills/prepare/SKILL.md) | Missingness, encoding, scaling, features and leakage-safe pipelines |
| [train](skills/train/SKILL.md) | Model families, tuning budgets, search and refit decisions |
| [validate](skills/validate/SKILL.md) | Frozen evaluation, errors, robustness and supported claims |
| [experiment](skills/experiment/SKILL.md) | Intervention design, A/B tests, power and causal limits |
| [release](skills/release/SKILL.md) | Reproducibility, packaging and authorized rollout |
| [operate](skills/operate/SKILL.md) | Monitoring, incident diagnosis, retraining and retirement |

The router loads the relevant skill and conditional references as needed. A small explanation need not create a project. End-to-end work records why each applicable stage was performed, deferred or inapplicable. Predictive validation and intervention experiments answer different questions.

## Expected project output

Notebooks follow the problem's questions and results, with explanations where they help the reader. The lifecycle guides the analysis without imposing identical headings or a Markdown block around every cell. Detailed coverage and run records can live in linked reports; consequential assumptions and limitations stay beside the findings they qualify.

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
  1ml/state.json            # workflow decisions
  runs/01-ingestion/
    shipment-delay.ipynb     # notebook-only history
```

Data may stay in its authorized database, URL, dataframe or local format. CSV export is not a prerequisite. Immutable inputs are shared; previous notebooks record source/dependency versions for reconstruction without historical model weights or duplicate environments. Paths, package installation and verification must work from the documented project location. See the [notebook protocol](references/notebook-protocol.md).

## Runtime and boundaries

Python helpers require **Python 3.10+**:

```sh
python -m pip install -r requirements.txt
```

Use a chosen environment. Modeling and notebook-execution dependencies are task-specific; the agent must record them in the learner project's requirements and provide a runnable installation cell. No datasets, credentials, paid model access, cloud services, or AutoML engine are bundled.

Helpers cover state, notebook cells, rules and basic profiling. The acquisition skill supports broader source-loading decisions than the profiler CLI. See [setup](references/setup.md) and [capability boundaries](references/capabilities.md). External writes, competition submissions and deployments require the user's authorization.

## Verification and development

```sh
python tools/validate_plugin.py
python -m unittest discover -s tests -t .
```

Optional notebook integration checks need [requirements-test.txt](requirements-test.txt); missing optional dependencies produce skips. A writable `TMP`/`TEMP` may be needed on restricted Windows hosts. Validate Claude packaging with `claude plugin validate .`.

Tests check implementation mechanics. [Scenario cases](tests/scenarios/decision-paths.md) and [behavioral evaluations](tests/evals/README.md) assess agent decisions separately. [Observed FCC/NVIDIA results](tests/evals/results-summary.md) include failures despite correct skill reads. Fresh Astra evaluations have also exercised tabular, forecasting, clustering and notebook delivery workflows locally; those observations do not establish unattended reliability or cross-host certification.

Reusable verification code under `tests/` and `evals/` is maintainer tooling. Generated trials, notebooks, datasets, weights, local research and credentials are excluded from Git. The plugin works without ignored research or local evaluation results.

Account-connected maintainer automation is managed separately. Installing 1ml does not grant account access or start scheduled jobs.

## Contribute and release

`main` is the repository's default branch and contains the stable plugin; a normal clone and all installation commands follow it. Use `develop` for contributions: open focused pull requests against `develop`, with relevant checks and evidence. Release changes move through a `develop` → `main` pull request after the required checks pass.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and review expectations, [SECURITY.md](SECURITY.md) for private vulnerability reports, and [CHANGELOG.md](CHANGELOG.md) for releases.

## Distribution and license

The repository includes a Claude marketplace catalog and host packaging metadata. A GitHub push does **not** automatically submit it to curated marketplaces. See [installation and distribution](docs/installation.md).

[MIT license](LICENSE). Contributions should preserve selective loading, connected references, evidence-based decisions and runnable deliverables.
