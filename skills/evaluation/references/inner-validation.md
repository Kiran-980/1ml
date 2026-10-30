# inner validation

## 3.6 When a valid split is not feasible

| Conflict | Valid next action | Shortcut to reject |
|---|---|---|
| Too few groups to support the planned folds | Reduce fold count if meaningful, use a justified held-out group/site design, or collect more independent groups | Split rows from the same group merely to make CV run |
| Rare class occurs in only one group or late period | Report the unsupported class/generalization claim; acquire coverage or narrow the task | Move future/related examples into training to force class balance |
| Combining future time and unseen groups leaves too little data | Decide which deployment claim is supported; report separate known-entity/future and new-entity evaluations if those are genuinely different use cases | Claim both from a convenient random split |
| Outcome maturation leaves no recent labels | Evaluate older mature cohorts with a stated recency limitation and arrange prospective follow-up | Mark immature outcomes negative |
| No independent final sample remains | Use a suitable outer/nested evaluation if data/design permit, or produce provisional development evidence and collect a new cohort | Repeatedly inspect the same holdout while calling it untouched |
| Small dataset cannot sustain all tuning/calibration/policy roles | Reduce search/model flexibility, use a valid cross-fitting procedure, or omit unsupported probability/policy claims | Fit all adjustments on training predictions and report optimistic scores |

Record what changed in the evaluation contract. Reducing scope is a domain decision if it excludes an intended population. A splitter successfully returning indices is insufficient evidence that evaluation is meaningful.

Narrowing the population also changes the relevant split. New patients at already observed hospitals may require patient-disjoint evaluation while keeping those hospitals represented; leaving entire hospitals out still evaluates unseen hospitals. Do not recommend a hospital holdout as the repair for a known-hospital claim. With positives at only one site, holding that site out can also leave training without positives. Another positive site may make a score computable, but it does not by itself establish adequate independent coverage or precision.


## 3.7 Inner validation must respect the outer design

Audit every component that internally partitions data: target encoding, early stopping, calibrated classifiers, stacking, and threshold tuning. Supply group/time-aware folds and metadata at the correct nested level where supported. An outer grouped test does not make random inner selection/calibration the intended procedure, and an outer pipeline cannot automatically refit an already transformed matrix inside a component's own CV.

For example, place learned preprocessing inside the base estimator being cross-fitted when out-of-fold predictions are required. Otherwise an imputer/selector fitted before the internal CV may have seen its calibration/stacking validation rows. Keep the whole procedure inside the outer training partition. Stacking's internal CV creates meta-training predictions; it is not the outer performance evaluation. Prefit base models trained on the same meta-training records risk severe overfitting. [StackingClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html)

Some APIs expect each training example to receive exactly one out-of-fold prediction. Rolling temporal splits often leave an initial prefix without predictions; repeated folds assign several. Do not force these into an incompatible API by inventing future-informed predictions. Use a supported procedure or explicit history-only calibration/meta-training window with documented exclusions. [Out-of-fold prediction contract](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_predict.html)

For the final fitted/calibrated policy and its evaluation roles, continue to [the refit protocol](../../train/references/final-fitting.md#610-refitting-calibration-and-policy-order).
