# Choose task-specific guidance early

Load only profiles matching the current claim, before their assumptions affect data/labels/design. These are methodological guidance, not claims of prebuilt estimator implementations. Common tabular prediction can proceed without a specialist profile.

Choose by the target and observation process, not a domain keyword. Future transactions do not automatically make event-time classification a forecasting task. Repeated customer rows do not establish time-to-event censoring; few positive examples do not establish positive-only observation. Fraud may be ordinary supervised classification rather than anomaly detection. Routine label maturation can be handled by evaluation's label/split design. Load additional profiles only when their defining condition is present; state an unresolved condition instead of assuming it and loading every plausible branch.

| Trigger | Profile | First affected decision |
|---|---|---|
| Future values, horizons, seasonal/repeated series | [Forecasting](forecasting.md) | Prediction origin, available inputs, backtest |
| Incomplete event follow-up | [Survival](survival.md) | Outcome/censoring construction |
| Ordered items, recommendations, exposure-driven clicks | [Ranking](ranking.md) | Candidate set, logging and ranking utility |
| Effect of taking an action | [Causal](causal.md) | Identification, assignment, overlap |
| Unusual events or normal-only training | [Anomaly](anomaly.md) | Outlier versus novelty setup, labels/alert unit |
| Unlabeled groups or segments | [Clustering](clustering.md) | Similarity and usefulness |
| Few labels, positive-only observations, active collection | [Scarce labels](scarce-labels.md) | Observation/selection process |
| Text, images, audio, structured annotation | [Media](media.md) | Annotation and task-specific metrics |
| Generated answers or retrieval-grounded systems | [Generative](generative.md) | Evidence corpus, access, evaluation |
| Sequential decisions and feedback | [Sequential decisions](sequential-decisions.md) | Logged policy, exploration, evaluation feasibility |

Profiles may compose, such as forecasting with scarce labels; explicitly resolve incompatible assumptions. Return to the owning skill with task-specific constraints. If a specialist method is beyond validated tooling, identify the missing research/design/data step using [capability boundaries](../capabilities.md), rather than substituting an ordinary classifier.
