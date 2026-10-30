# 1ml — Free machine learning skills for AI coding agents

[![Validate 1ml](https://github.com/Kiran-980/1ml/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/Kiran-980/1ml/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Kiran-980/1ml)](https://github.com/Kiran-980/1ml/releases)

Build readable, reproducible machine learning notebooks with **Codex, Claude Code and other coding agents**. Twelve connected skills guide classification, regression, time series forecasting, clustering, exploratory data analysis and model evaluation.

1ml helps your agent choose useful baselines, prevent data leakage and explain what the results actually support. It can also conclude that a rule, statistical analysis or existing baseline is enough.

**Free and open source under MIT.** No 1ml subscription, account or paid tier is required. Your coding agent, model provider and compute may have their own costs.

[Website](https://kiran-980.github.io/1ml/) · [Install](#install) · [Try your first project](docs/getting-started.md) · [See examples](docs/examples.md) · [Browse ML tasks](docs/machine-learning-skills.md) · [Contribute](CONTRIBUTING.md)

## See what you can make

[**Can tweet text identify real disasters?**](https://www.kaggle.com/code/kiranganaparapu/can-tweet-text-identify-real-disasters) is a public text-classification notebook made with 1ml. Read the analysis on Kaggle to see the output, then use the [example guide](docs/examples.md) to start your own classification, regression or forecasting project. One notebook is an example, not a guarantee of future results.

Notebooks follow the problem's questions and findings. The lifecycle guides the work without forcing identical headings or a Markdown block around every cell.

## Install

### Claude Code

Run inside Claude Code:

```text
/plugin marketplace add Kiran-980/1ml#main
/plugin install 1ml@1ml
/1ml:lifecycle
```

### Codex

Run in your terminal with a Codex CLI version that supports plugins:

```sh
codex plugin marketplace add Kiran-980/1ml --ref main
codex plugin add 1ml@1ml
```

Start a fresh session and select **1ml:lifecycle** in the skill picker, or ask Codex to use it.

Then give the agent a concrete task:

> Use 1ml to investigate customer churn in `customers.csv`. First check the target, when each feature becomes available, and whether customers repeat. Choose a suitable validation split, compare a simple baseline with justified models, and explain false positives and false negatives. Deliver an executed notebook with concise findings and reproducible dependencies.

No dataset ready? Follow the [small synthetic first project](docs/getting-started.md), which needs no dataset download or competition account.

**Other agents:** installation routes are documented for [OpenCode](docs/installation.md#opencode), [Gemini CLI](docs/installation.md#gemini-cli), [Pi](docs/installation.md#pi) and [Hermes](docs/installation.md#hermes). Native installation and discovery were verified in Codex and Claude Code; other routes are not end-to-end certified. Keep the complete repository together so shared references work.

See the [installation guide](docs/installation.md) for verification, local alternatives and [automatic updates](docs/installation.md#automatic-updates). All published installation commands follow `main`.

## Choose a machine learning task

| Task | What the skills help you decide |
| --- | --- |
| [Classification](docs/machine-learning-skills.md#classification-skills) | Labels, class imbalance, precision/recall, calibration and appropriate validation |
| [Regression](docs/machine-learning-skills.md#regression-skills) | Numeric targets, simple baselines, MAE/RMSE and residual analysis |
| [Time series forecasting](docs/machine-learning-skills.md#time-series-forecasting-skills) | Forecast horizon, chronological backtesting, seasonal baselines and available features |
| [Clustering](docs/machine-learning-skills.md#clustering-and-unsupervised-learning-skills) | Scaling, distance, stability and whether groups answer a useful question |
| [EDA, statistics and model evaluation](docs/machine-learning-skills.md#data-analysis-statistics-and-model-evaluation) | Missingness, useful charts, uncertainty, cross-validation and error analysis |

## Connected, independently usable skills

| Skill | Purpose |
| --- | --- |
| [lifecycle](skills/lifecycle/SKILL.md) | Start or resume a project and choose the next useful step |
| [frame](skills/frame/SKILL.md) | Define the question, learning task and no-ML alternatives |
| [data](skills/data/SKILL.md) | Collect, load, join and inspect data |
| [evaluation](skills/evaluation/SKILL.md) | Define metrics, baselines and time/group boundaries |
| [explore](skills/explore/SKILL.md) | Investigate distributions, relationships and anomalies |
| [statistics](skills/statistics/SKILL.md) | Estimate effects and uncertainty |
| [prepare](skills/prepare/SKILL.md) | Build preprocessing and features without leakage |
| [train](skills/train/SKILL.md) | Compare models and manage tuning budgets |
| [validate](skills/validate/SKILL.md) | Evaluate frozen models and review supported claims |
| [experiment](skills/experiment/SKILL.md) | Design randomized experiments and A/B tests |
| [release](skills/release/SKILL.md) | Package reproducible results and authorized releases |
| [operate](skills/operate/SKILL.md) | Monitor, diagnose and decide when to retrain |

The agent loads relevant instructions as needed. A small explanation need not create a project. Generative AI workflows are outside the current focus.

## What to expect

A project can include an executed notebook, requirements, metrics, predictions and a regenerable model. The agent chooses a descriptive notebook name and keeps consequential assumptions beside the findings. See [project outputs and verification](docs/project-output.md).

1ml supplies instructions and supporting Python helpers, not a hosted AutoML service or a model. The helpers require **Python 3.10+**; project dependencies are chosen and recorded by the agent. Installing 1ml does not start jobs or grant access to any account. Competition submissions, external writes and deployments require your authorization.

Mechanical tests and installation checks do not establish scientific correctness. The [evaluation guide](tests/evals/README.md) and [observed results](tests/evals/results-summary.md) document the evidence and remaining limitations.

## Help improve 1ml

Try a real problem, share a reproducible example or report a specific failure. Improvements to notebook clarity, validation, task coverage and agent compatibility are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution ideas and checks; use [SECURITY.md](SECURITY.md) for private security reports.

`main` is the stable default branch. Send contributions to `develop`; releases reach `main` after required checks pass. See the [changelog](CHANGELOG.md) and [releases](https://github.com/Kiran-980/1ml/releases).

If 1ml helped you, sharing your notebook with a link to this repository helps other people find it. Starring the repository is optional and helps you find it again.

[MIT license](LICENSE). You can use, modify and redistribute 1ml under its license terms. The repository includes its own marketplace catalog; it is not automatically listed in curated directories.
