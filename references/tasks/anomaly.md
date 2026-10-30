# anomaly

## Anomaly versus novelty detection

**Documented:** Outlier detection fits possibly contaminated data; novelty detection assumes a clean reference set and scores new observations. LOF's default outlier mode differs from `novelty=True`, whose scoring must be applied to unseen samples. Detector thresholds and anomaly scores are not automatically event probabilities. [scikit-learn novelty and outlier detection](https://scikit-learn.org/stable/modules/outlier_detection.html)

**Decision synthesis:** If representative labeled anomalies exist, compare supervised cost-sensitive detection. If clean normal history exists, compare novelty methods; if contamination is uncertain, compare robust/outlier methods and record assumptions. Choose representations and distances appropriate to the domain. Validate precision at review capacity, event-level recall and detection delay when labels permit, and false alerts per operational unit. Without labels, expert review and stability checks support a pilot, not a verified accuracy claim. A rare observation can be valid; investigation precedes deletion. Set thresholds with validation evidence and analyst capacity, not an assumed universal contamination percentage.

### Concrete anomaly candidates

For tabular anomaly screening, compare a domain rule with isolation-based detection when random-partition isolation is a plausible useful signal; evaluate the resulting alerts, not just its score distribution. [Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html). When unusualness is relative to local neighborhoods, LOF is a candidate only if the representation/scale/neighbor metric is meaningful; honor its distinct outlier versus unseen-point novelty modes. [LOF](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html)

If neither produces a useful review queue, inspect representation, reference contamination, and what 'anomalous' means; acquire expert labels rather than trying to force a contamination fraction. When events span many records, define alert merging, event matching, and detection delay before scoring. Route confirmed representative positive/negative labels back to supervised comparison.
