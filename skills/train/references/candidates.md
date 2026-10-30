# candidates

## 6.1 Select candidates, then earn the selection with evidence

The estimator chart is a rough candidate guide with 'try next' routes. It is not a proof that one family is optimal above/below a row threshold. [Scikit-learn estimator map](https://scikit-learn.org/stable/machine_learning_map.html)

Use this sequence for a predictive benchmark:

1. Confirm the task, output type, metric/policy, split, label support, and feature timing from the framing, acquisition, and evaluation contracts.
2. Establish the current process and a trivial statistical baseline: majority/prior, mean/median, naive seasonal forecast, popularity, or domain rule as appropriate.
3. Characterize independent sample count, features, sparsity, modality, missingness, cardinality, dependence, output constraints, and available compute.
4. Choose a small set of meaningfully different candidates with explicit hypotheses. For example: regularized linear for a cheap stable baseline; additive/spline terms for smooth effects; boosting for interactions. A candidate may be ruled out by serving or data constraints before training.
5. Compare complete pipelines with consistent evaluation and documented budgets. Inspect both aggregate and important-slice errors.
6. Expand complexity only when a measured deficiency suggests a plausible remedy. Stop, collect data, or keep a simpler method if no justified gain appears.

This is an experimental strategy, not a mandatory tournament of every library class. Record rejected candidates and reasons so future agents do not repeat unhelpful searches.


## 6.2 Linear versus nonlinear is not decided by one test

A linear model is linear in its fitted parameters; polynomial terms, splines, and interactions can represent nonlinear relationships in original inputs. Logistic regression has a linear predictor in log-odds, not a linear probability curve. Pairwise correlations can miss interactions and curved relationships, while a visually curved plot may reflect confounding or mixtures.

Compare: a domain-appropriate regularized linear model, useful basis expansions/additive structure when justified, and a nonlinear family when resources allow. Inspect out-of-fold residual/error patterns and actual deployment constraints. If the nonlinear candidate improves only training scores, diagnose overfitting or leakage instead of treating complexity as progress. If scores are practically indistinguishable within uncertainty, prefer the feasible system with lower total cost, explaining the tradeoff.

The need to extrapolate changes the comparison. Many local/tree methods have limited extrapolation behavior; linear trends also extrapolate badly when their assumptions fail. Evaluate realistic ranges and state unsupported regions. A monotonic domain rule can motivate a constrained estimator, but constrain only what the domain actually supports.


## 6.3 Candidate families and the situations that justify them

| Family | Why include it | What can make it unsuitable or require a change |
|---|---|---|
| Ridge / regularized logistic | Stable, inexpensive baseline; correlated features; sparse linear signal | Missed interactions/shape, availability of calibrated probabilities, scaling and penalty selection |
| Lasso / elastic net | Sparse signal hypothesis or feature-cost pressure | Correlated predictors can destabilize selected variables; evaluate stability and held-out loss |
| Robust/quantile regression | Outlier-resistant objective or asymmetric decision | A robust objective changes what is estimated; valid costly extremes may still matter |
| Poisson/Gamma/Tweedie GLM | Outcome domain and variance/loss structure match counts, positive amounts, or mixed zero-positive amounts | Exposure, overdispersion, structural zeros, link assumptions and appropriate metric |
| Linear SVM / SGD linear learner | High-dimensional sparse inputs, large/streaming data | Scaling, convergence, loss/output compatibility; scores may not be probabilities |
| Kernel SVM/SVR | Nonlinear smooth boundary with feasible sample/kernel cost | Scaling and C/kernel tuning; training/support-vector memory and serving latency |
| K-nearest neighbors | Local similarity is meaningful; useful simple comparison | Scale, irrelevant dimensions, memory, inference cost, weak extrapolation |
| Naive Bayes | Fast text/count/binary or suitable generative baseline | Variant must match feature domain; independence is conditional on class; probabilities may be poorly calibrated |
| LDA/QDA | Class-conditional Gaussian structure is plausible | Covariance estimation/sample support; shared covariance for LDA, more parameters for QDA |
| Small decision tree | Compact nonlinear rule baseline | Instability, depth/leaf support, overfitting; readability declines with size |
| Random forest / extra trees | Nonlinear interactions with comparatively low preprocessing burden | Memory/latency, extrapolation, weak sparse high-dimensional suitability in some tasks |
| Gradient/histogram boosting | Flexible tabular patterns and interactions | Learning rate/iterations/leaves, leakage in early stopping, categorical/version limits |
| Gaussian process | Modest-size problem with useful kernel prior and probabilistic modeling | Computational cost, dimensionality, kernel/noise assumptions; uncertainty is model-dependent |
| Neural network | Rich nonlinear structure or task-specific representation learning | Data/compute, scaling, seed sensitivity, tuning, overfitting and deployment complexity |
| Voting/averaging/stacking | Complementary validated errors | More latency/maintenance; stacking needs out-of-fold training predictions |

Primary method references: [Linear models and GLMs](https://scikit-learn.org/stable/modules/linear_model.html), [SVM](https://scikit-learn.org/stable/modules/svm.html), [Neighbors](https://scikit-learn.org/stable/modules/neighbors.html), [Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html), [LDA/QDA](https://scikit-learn.org/stable/modules/lda_qda.html), [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html), [Gaussian processes](https://scikit-learn.org/stable/modules/gaussian_process.html), [MLP](https://scikit-learn.org/stable/modules/neural_networks_supervised.html).

The table's workflow recommendations are synthesis. A family's inclusion is a hypothesis to test, not an endorsement on every dataset. Verify estimator support for missing values, sparse input, sample weights, multioutput targets, categorical features, monotonic constraints, and probability outputs in the installed version. Similar names do not guarantee equivalent capabilities.

### Resolve response-domain and sample-shape constraints before search

For counts with known positive exposure, distinguish modeling counts with a log-exposure offset from modeling rates with an appropriate exposure-weighted loss. Statsmodels' GLM exposure adds log(exposure) with coefficient fixed at one under a log link. Scikit-learn demonstrates Poisson frequency modeling using count/exposure with exposure weights. Do not double-count exposure or assume an arbitrary weight parameter has the same semantics. Investigate zero/invalid exposures before fitting; convert a predicted rate to the requested count horizon using the appropriate exposure. [GLM exposure](https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html), [Poisson rate example](https://scikit-learn.org/stable/auto_examples/linear_model/plot_poisson_regression_non_normal_loss.html)

If zero counts are ordinary sampling outcomes, a count model already allows them. A hurdle/zero-inflated mechanism requires evidence for distinct occurrence/amount or structural-zero processes, not merely a large observed zero percentage. Compare the complete predictive distribution/decision, inspecting dispersion and exposure first. Strictly positive amounts and zero-plus-positive amounts need different domains; use the [task/metric contract](../../evaluation/references/task-contract.md) to choose an appropriate candidate family. An invalid negative prediction is a model/policy failure to address explicitly, not a row to omit silently from scoring.

When features substantially outnumber independent examples, start with a constrained/regularized or suitable pretrained representation and controlled search; a feature-rich table is not automatically rich evidence. When a model is numerically singular or a class is absent, fix the design/support or use a justified alternative, rather than interpreting successful solver termination as sufficient evidence. If an ordered, joint-output, or unknown-class task is selected, resolve the corresponding [target branch](../../evaluation/references/metrics-policy.md#28-resolve-target-types-that-do-not-fit-a-default-classifier) before applying this chapter's generic family table.


## 6.4 Large data, many features, and the supplied SVG

The supplied chart includes 50/10,000/100,000-sample thresholds, SGD, kernel approximation, sparse regression, clustering, and manifold branches. Treat these as historical navigation cues. Feasibility depends jointly on n, p, sparsity, independent units, kernel storage, hyperparameter trials, hardware, and prediction frequency. Its 'get more data' branch needs the acquisition reasoning in chapter 1; its terminal 'tough luck' becomes reframe, non-ML, acquire, or seek method-specific research.

When full batch training is infeasible, inspect bottlenecks before choosing an incremental estimator. Incremental learning requires streaming data, stable feature extraction, and an estimator supporting updates. Maintain schema/class handling and evaluation against a consistent held-out population. Evolving preprocessing can change feature meaning between batches. [Scaling strategies](https://scikit-learn.org/stable/computing/scaling_strategies.html)

Kernel approximation can combine explicit approximate features with an efficient linear learner. Compare approximation dimension, seed, resource use, and quality against a feasible exact or alternate nonlinear baseline. [Kernel approximation](https://scikit-learn.org/stable/modules/kernel_approximation.html)

For dimensionality reduction, first state whether the purpose is visualization, compression, denoising, speed, or predictive improvement. PCA/SVD are baselines; random projection offers approximate distance preservation with a dimension/distortion tradeoff. A geometric guarantee does not guarantee preserved prediction quality. [Random projection](https://scikit-learn.org/stable/modules/random_projection.html)

Isomap/LLE/spectral embedding and t-SNE impose different geometry and computational assumptions. Visual separation is not proof of true classes; lack of separation in two dimensions does not disprove predictability. t-SNE emphasizes local structure and does not preserve global geometry reliably. Confirm new-point transformation support before using an embedding in a serving pipeline. [Manifold learning](https://scikit-learn.org/stable/modules/manifold.html)

Chart labels are not API contracts: resolve labels such as Randomized PCA and VBGMM to current supported implementations/configurations instead of copying them as class names. Model-specific reference lookup is required before coding.
