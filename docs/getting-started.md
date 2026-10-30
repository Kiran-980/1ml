# Your first machine learning notebook with 1ml

[1ml](../README.md) is a free collection of machine learning skills for coding agents. This small example gives you a way to try the workflow before connecting a real dataset.

## Install and choose a working folder

Follow the [installation guide](installation.md) for your agent, then open a new project folder outside the plugin checkout. Select `1ml:lifecycle`, or ask your agent to load it. The agent needs permission to write files and run Python in that folder.

There is no 1ml account or subscription. Your agent/model service and compute have their own requirements and possible costs. Installing Python dependencies can require internet access.

## Try a small classification problem

Copy this request into your agent:

> Use 1ml to make a small, reproducible binary-classification notebook in this project folder. Generate 1,000 synthetic rows with scikit-learn's `make_classification`, 10 features, 5 informative features, class weights [0.8, 0.2], and random_state=42. Explain that the data is synthetic and is not evidence of real-world performance. Define the positive class as label 1. Reserve a stratified 20% final test set before fitting anything. On the training portion, compare a most-frequent dummy baseline with logistic regression in a StandardScaler pipeline using stratified cross-validation. Use average precision to compare ranking quality and report precision/recall at the default decision threshold separately. Freeze the approach before evaluating the final test once. Include a relevant chart, measured results and limitations. Produce an executed notebook with a descriptive title and dependency versions. Keep the explanation short and specific to the problem; do not submit, publish or deploy anything.

This is a starter prompt, not a pre-executed benchmark. Your agent chooses the implementation and may need to install dependencies. Runtime and model output depend on your environment.

## Check the result

Open the delivered notebook and check that:

- All cells ran, charts are visible and the conclusion uses the measured results.
- Preprocessing is fitted inside each training fold; the final test set is not used to select models or thresholds.
- The dummy baseline and logistic regression use the same evaluation design.
- The notebook says what the synthetic example cannot establish.
- Dependencies and any supporting files let you rerun it from the project folder.

If an execution error remains, ask the agent to reproduce and repair that error. A plausible explanation or an unexecuted notebook is not proof that the project works.

## Move to your own data

Replace the synthetic-data request with your dataset location and the decision you want to support. Describe what one row means, what to predict, when the prediction happens, and whether entities repeat over time. These details determine the split and which features are valid.

For other tasks, use the [classification, regression and forecasting examples](examples.md) or [full ML task guide](machine-learning-skills.md). The [project-output guide](project-output.md) explains the delivered files.
