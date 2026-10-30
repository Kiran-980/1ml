# feasibility

## 1.1 Start with evidence already in the project

Inspect the project description, existing notebooks, data dictionaries, schemas, queries, sample files, evaluation reports, and deployed decision process. Record what exists and what is inferred. Ask the user only for information the evidence cannot establish: intended action, acceptable costs, access, domain meaning, and ownership. An identifier-like column name does not establish the unit of analysis; a numeric dtype does not establish a continuous measurement.

Create a compact intake record:

| Field | Evidence required | Consequence when missing |
|---|---|---|
| Decision and owner | Who acts, what action changes, and when | Clarify the use case before optimizing a model |
| Population and unit | Customer, transaction, device, document, session, or other unit | Audit keys, repeated observations, and selection mechanism |
| Current process | Rules, expert judgment, search, existing model, or no action | Establish a measurable baseline |
| Desired outcome | Observable benefit and measurement window | Design outcome collection; distinguish proxy from business result |
| Constraints | Latency, capacity, cost, interpretability, data access, acceptable failures | Eliminate infeasible approaches early |
| Data and labels | Sources, historical coverage, provenance, availability times, quality | Inspect or acquire rather than assuming readiness |
| Evaluation owner | Person/process that can judge errors and consequences | Treat uncertain outputs as a pilot, not validated automation |

An ML lifecycle is iterative: failed evaluation can send the project back to framing or data collection. Google's engineering guidance emphasizes simple baselines and reliable infrastructure before unnecessary complexity. [AWS lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lifecycle.html), [Google Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)


## 1.2 Decide whether ML belongs in the solution

| Business need or observation | First route to compare | Evidence required to choose ML |
|---|---|---|
| Exact lookup, reconciliation, arithmetic, permissions, deterministic rules | SQL, lookup tables, validation rules, ordinary software | A genuinely uncertain mapping remains after deterministic work |
| Understand historical performance | Descriptive statistics, dashboard, cohort analysis | A future prediction or decision adds value beyond reporting |
| Schedule or allocate under known costs and constraints | Optimization, operations research, simulation | Unknown quantities need estimates; prediction may feed the optimizer |
| Explain what an intervention will change | Randomized experiment or defensible causal design | Identification assumptions support an effect estimate |
| Search an existing knowledge base | Search, retrieval, extractive answers | Semantic inference or generation improves a measured user task |
| Common language/vision task with little local data | Existing pretrained model, rules, or human workflow | Local evaluation supports transfer and task/data rights permit use |
| Predict an observable outcome from historical inputs | Supervised baseline | Inputs precede outcomes, independent evaluation is possible, and gain exceeds cost |
| Find unusual events without trustworthy labels | Rules and an expert-reviewed anomaly pilot | Review data establish useful alerts at operational capacity |
| Very little independent evidence or unreliable outcomes | Instrumentation, annotation, expert process | Collection produces adequate coverage and uncertainty for the decision |
| Current baseline meets requirements cheaply | Keep the baseline | New complexity delivers meaningful, sustainable benefit |

This table is a decision framework, not a ranking of technologies. Mixed systems are common: a forecast supplies demand to an optimizer; business rules limit model actions; retrieval supplies evidence to a language model.

Check seven feasibility questions before substantial training:

1. **Actionability:** What changes because of the output? Who can act within the prediction horizon?
2. **Information:** Will every proposed input exist at that exact time in production?
3. **Evaluation:** Can outcomes or expert judgments be obtained without circular labels?
4. **Coverage:** Does the dataset represent intended entities, conditions, rare cases, and time periods?
5. **Economics:** Is expected benefit plausible after data, compute, review, integration, and maintenance costs?
6. **Operations:** Can the system handle missing inputs, latency, failures, and model updates?
7. **Impact:** Which errors harm which groups, and who accepts the operating policy?

Use a stop condition when a critical answer is unsupported. Examples: no action owner; a label cannot be observed; all predictive features are post-outcome; evaluation data contain only accepted applicants but deployment covers all applicants; a small improvement cannot repay review costs. Risk management should span design through operation rather than appear only at release. NIST's framework supplies governance concepts, not certification of a particular model. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)


## 1.3 Data sufficiency has no universal row threshold

Count independent units, outcomes per class, group/time coverage, and effective deployment diversity, not just rows. A million sensor readings from two devices cannot establish performance on a fleet of new devices. Ten positive events cannot support precise subgroup recall just because negatives are abundant.

Use learning curves, uncertainty around decision-relevant metrics, label audits, and coverage gaps to decide what to collect next. Improvement with additional representative data is evidence for collection; a flat curve may instead reflect noisy labels, weak representation, a restrictive model, or distribution mismatch. Curves diagnose possibilities, not a unique cause. [Learning curves](https://scikit-learn.org/stable/modules/learning_curve.html)

Synthetic data can test plumbing, explore assumptions, or augment a supported training process. It does not establish real-world performance without independent real evaluation. Transfer learning can reduce labeling needs but still requires local validation. If evaluation itself is too weak, label a representative test sample before spending the budget on tuning.
