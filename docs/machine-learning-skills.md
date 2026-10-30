# Machine learning skills for classification, regression and time series

[1ml](../README.md) gives AI coding agents twelve connected machine learning skills for data analysis, modeling and reproducible Jupyter notebooks. Start with the [lifecycle skill](../skills/lifecycle/SKILL.md), or use an individual skill for a focused decision. Follow the [installation guide](installation.md) for Codex, Claude Code and other supported agent integrations.

1ml is free and open source. Start with a [small synthetic project](getting-started.md), or see a [public notebook and task-specific starter prompts](examples.md). Your agent/model service and compute may have their own costs.

## Classification skills

Classification predicts a category, such as customer churn, equipment failure or the class of a document. Binary classification and multiclass classification need an explicit label definition and a validation split that matches how predictions will be used.

1ml guides label checks, class imbalance, baselines, preprocessing and model evaluation. Choose accuracy, precision, recall, F1, ROC AUC or another justified metric according to the task. Keep repeated entities together when deployment involves new people, machines or customers; do not assume a random row split is appropriate.

> Use 1ml to build a customer-churn classification notebook. Check what information is available when the prediction is made, define a leakage-safe split, and compare a simple baseline with justified classifiers. Explain false positives and false negatives using measured results.

Relevant skills: [frame](../skills/frame/SKILL.md), [evaluation](../skills/evaluation/SKILL.md), [train](../skills/train/SKILL.md), [validate](../skills/validate/SKILL.md).

## Regression skills

Regression predicts a numeric value, such as a house price, delivery duration or energy demand. The target's units and the cost of errors determine whether metrics such as MAE or RMSE are useful. Transformations and outliers require explicit decisions, and preprocessing must be fitted on training data only.

> Use 1ml to compare baselines and regression models for house prices. Inspect missing values and target skew, justify the metric, keep preprocessing inside each training fold, and analyze large errors. Produce a reproducible notebook with an honest conclusion.

Relevant skills: [explore](../skills/explore/SKILL.md), [prepare](../skills/prepare/SKILL.md), [train](../skills/train/SKILL.md), [validate](../skills/validate/SKILL.md).

## Time series forecasting skills

Time series forecasting predicts future observations. Define the forecast origin, horizon and information available at that origin before constructing lag or rolling features. Use chronological evaluation or rolling backtests and compare against suitable naive or seasonal baselines. A random train/test split can leak future information.

> Use 1ml to forecast daily sales for the next 14 days. Define the forecast origin and available features, compare seasonal baselines, and run chronological backtests. Explain how the model behaves across different periods and document the limits of the evidence.

Relevant skills: [evaluation](../skills/evaluation/SKILL.md), [prepare](../skills/prepare/SKILL.md), [train](../skills/train/SKILL.md), [operate](../skills/operate/SKILL.md).

## Clustering and unsupervised learning skills

Clustering explores groups without a known target label. Feature scaling, distance metrics and the intended use of the groups matter. A visually attractive separation or a high internal score alone does not establish useful customer segments or real-world categories.

> Use 1ml to investigate customer segments. Decide whether clustering is useful, justify the features and scaling, compare reasonable methods, and check stability. Explain what the groups do and do not support.

Relevant skills: [frame](../skills/frame/SKILL.md), [explore](../skills/explore/SKILL.md), [prepare](../skills/prepare/SKILL.md), [validate](../skills/validate/SKILL.md).

## Data analysis, statistics and model evaluation

Use individual skills for exploratory data analysis, missing-data investigation, feature engineering, statistical uncertainty, cross-validation or error analysis. The [statistics skill](../skills/statistics/SKILL.md) covers estimates and uncertainty; the [experiment skill](../skills/experiment/SKILL.md) handles randomized interventions and A/B tests. Predictive performance and causal effects are different claims.

The [notebook protocol](../references/notebook-protocol.md) keeps explanations near consequential decisions and results. Notebooks follow the problem rather than repeating a fixed set of lifecycle headings. The agent should report measured findings, preserve meaningful limitations and choose a descriptive notebook title.

## Is 1ml an AutoML library?

1ml is a collection of agent skills and supporting helpers, not a bundled model-training service. The coding agent selects and implements suitable tools, including pandas and scikit-learn when appropriate. Project dependencies and execution requirements belong in the delivered project. It does not guarantee a particular score or perform account-connected submissions merely by being installed.

## Install or contribute

- [Install 1ml](installation.md) in your coding agent.
- [Browse all twelve machine learning skills](../README.md#connected-independently-usable-skills).
- [Contribute a focused improvement](../CONTRIBUTING.md) with evidence and relevant verification.

1ml is free to use under the [MIT license](../LICENSE). Preserve its copyright and license notice when redistributing it.
