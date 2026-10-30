# packaging rollout

## 9.1 Decide whether and how to serve the result

Deployment architecture follows the action's timing and workload. A periodic report may need only a reproducible batch job; a real-time decision needs a service contract and failure handling. Do not turn every trained model into an API by default.

| Mode | When it fits | Questions before choosing |
|---|---|---|
| Notebook/report | Analysis supports a human decision | Can someone reproduce it? Are conclusions and limits clear? |
| Batch scoring | Decisions tolerate delay and arrive in groups | Data cutoff, job duration, stale-output policy, retries, idempotency |
| Online service | Individual decisions need low latency | End-to-end latency, availability, feature access, concurrency, fallback |
| Streaming | State evolves continuously from events | Event ordering, lateness, replay, windows, state recovery |
| Edge/on-device | Connectivity/privacy/latency favors local execution | Memory/compute, device variation, update/rollback, version visibility |
| Human-assisted | Review adds necessary judgment or manages uncertainty | Capacity, response time, error escalation, human automation bias |

The inference contract specifies schema, types, units, feature timestamps/freshness, identity, output meaning, calibrated/policy version, error codes, and unsupported inputs. Training/serving share the same transformation definitions and compatible artifacts. A feature-store lookup or API success does not guarantee semantic parity.


## 9.2 Package a reproducible and trustworthy bundle

Bundle the fitted preprocessing and estimator, label mapping, calibration, threshold/decision policy, schema, dependency/environment specification, data/code provenance, selection evidence, and expected input/output examples. Add retrieval corpus/index/prompt/model settings for generative systems. Record training cutoff and intended use.

For file-based inputs, include the reader contract (delimiter/encoding, null tokens and dtypes) alongside the fitted model. A dataframe-only prediction test misses parser-induced category loss. Replay representative raw records through the documented reader and reloaded model, including the [absence/unknown token checks](../../data/references/acquisition.md#csv-tokens-with-domain-meaning) when applicable, and compare predictions with the original path.

Loading pickle/joblib-like artifacts can execute code; load only trusted artifacts. Environment/library compatibility matters, and cross-version restoration is not generally guaranteed. Alternative formats have coverage and conversion constraints; validate numerical/policy parity after conversion. [Scikit-learn persistence](https://scikit-learn.org/stable/model_persistence.html)

Use versioned runs/artifacts and explicit deployment references so the team can answer which data/code/model/policy produced a prediction. A registry is one implementation option; a small project can use a simpler controlled manifest if it preserves the needed evidence. [MLflow tracking](https://mlflow.org/docs/latest/ml/tracking/)


## 9.3 Roll out with observable behavior

Before exposure, replay representative requests through the packaged system, test dependencies and fallbacks, benchmark actual latency/memory, and exercise rollback. Shadow evaluation can reveal feature/serving differences. A staged/canary rollout limits exposure while monitoring quality and reliability. Rollback must restore a compatible model, transformations, schema, and policy, not just replace one weights file. [Deployment guardrail concepts](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails.html)

Define operator, alerts, escalation, rollback criteria, and fallback behavior before release. Monitor failed predictions and rejected inputs in denominators; a dashboard of only successful requests can hide a damaging failure mode. Keep logs sufficient for replay and outcome joining while limiting sensitive content and retention to the project's actual needs.

### Failure handling must define what the user actually receives

For a missing/stale source, timeout, invalid output, or overloaded reviewer queue, specify whether to use a validated simpler model/rule, return a bounded stale result, defer to review, or decline the decision. Set maximum staleness/queue delay where applicable. Do not turn every failure into a plausible default prediction. Record that fallback was used so its outcomes and cost can be evaluated separately and in the total system.

Rollback helps a bad model/service release only if the restored bundle and dependencies remain compatible. It does not repair an upstream unit change affecting both old and new models. Test the relevant boundary and route upstream failures to source repair or a fallback that does not depend on the broken source. Stopping unsafe or meaningless output can be a correct operational result.
