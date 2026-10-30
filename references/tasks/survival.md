# survival

## Survival, censoring, and competing events

**Documented:** An event-free record at last follow-up is censored: its event time is unknown beyond the observed duration. The outcome needs both duration and event indicator. Ordinary regression treating the censoring time as the event time loses this distinction. [scikit-survival introduction](https://scikit-survival.readthedocs.io/en/stable/user_guide/00-introduction.html)

**Decision synthesis:** Route time-to-event questions with incomplete follow-up here, including churn, default, and equipment failure. Define time origin, eligibility, event, censoring, and prediction horizon before selecting a model. Start with a population survival baseline; compare Cox-family and flexible survival estimators as assumptions/data support. If only fixed-horizon classification is needed, require correctly observed labels at that horizon or a censoring-aware method. Left truncation, interval censoring, recurrent events, time-varying covariates, and informative censoring require dedicated methods and statistical review.

**Documented validation:** Harrell's concordance can be optimistic under heavy censoring; IPCW concordance is an alternative. Dynamic AUC targets discrimination at selected times; time-dependent Brier scores evaluate probability predictions. IPCW evaluation requires appropriate censoring support. [Survival evaluation](https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html)

**Documented competing-risk branch:** When one event prevents another, event-specific cumulative incidence differs from treating every competing event as ordinary censoring. [Competing risks](https://scikit-survival.readthedocs.io/en/stable/user_guide/competing-risks.html)

**Decision synthesis:** Retain event types and choose the estimand first: cause-specific hazard, event probability, or overall survival. Report uncertainty and horizon-specific calibration, not just a risk ranking.
