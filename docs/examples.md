# Machine learning notebook examples and starter prompts

[1ml](../README.md) helps a coding agent turn a question and data into a reproducible analysis. This page separates an existing public notebook from prompts you can use to start new projects.

## Read a public classification notebook

[**Can tweet text identify real disasters?**](https://www.kaggle.com/code/kiranganaparapu/can-tweet-text-identify-real-disasters) is a text-classification notebook made with 1ml for Kaggle's [Natural Language Processing with Disaster Tweets](https://www.kaggle.com/competitions/nlp-getting-started) problem.

The question is whether a tweet describes a real disaster. Look at how text becomes model features, how a baseline is evaluated and how the notebook explains its findings. This is one observed example; it does not certify the plugin across models, datasets or agent hosts.

Reading a public notebook is separate from joining a competition. Downloading competition data or submitting predictions is subject to Kaggle's account requirements and competition rules. The plugin itself does not enroll you or submit anything when installed.

## Classification: customer churn

Use this when each prediction is a category and false positives and false negatives have different consequences.

> Use 1ml to investigate customer churn in `customers.csv`. Clarify what churn means and when a prediction will be made. Identify repeated customers, timestamps and features that reveal the outcome. Choose a validation split matching the intended use, compare a dummy baseline with suitable classifiers, and report ranking quality separately from threshold-specific precision and recall. Explain which mistakes matter. Deliver an executed notebook with measured findings and limitations.

Bring a target definition and a prediction time. If the same customer appears in multiple rows, a random row split may answer the wrong question. [Classification guidance](machine-learning-skills.md#classification-skills).

## Regression: house prices

Use this when the prediction is a number and its units affect the meaning of an error.

> Use 1ml to predict house sale prices from `houses.csv`. Check target units, missing values, unusual prices and whether location or sale date affects the split. Compare a median-price baseline with a regularized linear model and a justified tree model. Fit preprocessing inside the training folds. Choose the metric before tuning, show large residuals and explain what the final held-out result supports. Deliver an executed notebook and reproducible dependencies.

Bring the geography, period and intended use. Predicting future prices in a changing market requires a different evaluation from estimating missing prices in an existing sample. [Regression guidance](machine-learning-skills.md#regression-skills).

## Time series: daily demand

Use this when predictions must be made before future observations exist.

> Use 1ml to forecast daily demand from `daily-demand.csv` for the next 14 days. Check missing dates and whether zero demand differs from missing data. Define the forecast origin, horizon and features available at that origin. Compare a weekly seasonal-naive baseline with a justified forecasting model using chronological backtests. Keep the final period untouched until the approach is frozen. Show forecasts beside actual values and explain errors across periods. Deliver an executed notebook with reproducible dependencies.

Bring a time column, frequency, target and forecast horizon. Lag features in a multi-step forecast must not use the actual future target. [Time-series guidance](machine-learning-skills.md#time-series-forecasting-skills).

These three requests are starter prompts, not claims of completed experiments. For a small example without your own dataset, [start with synthetic classification](getting-started.md).

## Share an example

Contributions can link to a public notebook or provide a small reproducible example using appropriately licensed data. Explain the problem, data source, validation design and measured result. Include limitations and the versions needed to rerun it. Never publish credentials, personal data or competition files without permission. See [contribution guidance](../CONTRIBUTING.md).
