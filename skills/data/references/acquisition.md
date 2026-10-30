# acquisition

## 1.4 Collect or load data before making data-dependent choices

**Inputs:** approved local sources or connections, source documentation, resource budget, and a provisional question. **Outputs:** reproducible inventory, bounded dataframe or scalable equivalent, schema/profile, provenance, and an acquisition plan for gaps.

Preserve raw inputs. Use read-only queries for discovery, parameterize values, avoid printing credentials or sensitive records, and record extract time, query/version, filters, source timezone, and snapshot semantics. Load only necessary columns/rows for the current inspection. A first-rows preview is useful for parsing but is not a representative sample.

Choose the loader for the available source; a local download or CSV export is not a prerequisite. Reuse an existing dataframe, query an authorized database, or use a format-compatible URL reader/connector directly. Record reproducible loading code and source identity; keep a local snapshot/cache only when needed for reproducibility, access or performance. The bundled profiler CLI supports fewer sources than this workflow: use task-specific loading and dataframe inspection rather than converting a source solely to fit that helper.

| Format or situation | Initial action | Decision checks |
|---|---|---|
| Existing dataframe/table | Reuse the supplied object and recover its loading/query provenance | Prior filtering, mutations, schema, sampling and ability to reconstruct it in a fresh kernel |
| HTTP/object-storage URL | Use a reader or connector supporting the URI and actual data format | Access configuration, content/version identity, bounded loading and source changes between reads |
| CSV/TSV | Specify delimiter, encoding, null tokens, and important dtypes | Leading-zero IDs, decimal conventions, malformed rows, date ambiguity |
| Spreadsheet | Identify sheets, header rows, formulas, merged cells, and totals | Repeated headers, hidden assumptions, mixed units; distinguish data from presentation |
| Parquet/columnar | Inspect schema and select columns/partitions | Partition bias, schema evolution, dictionary/category consistency |
| JSON/events | Define normalization and array expansion | Preserve event/entity keys; explosion changes the observation unit |
| SQL | Inspect schema, keys, query plan where available, and bounded extract | Time consistency, filtering bias, joins, parameterization, access scope |
| Text/image/audio | Load a manifest of paths/IDs, metadata, and annotations | Corrupt content, duplicates, licensing, subject/source groups, label ontology |
| API/paginated source | Record request/filter/version and resume token | Rate limits, duplicate pages, changing snapshots, retries, idempotent ingest |
| Too large for memory | Select less data, aggregate, stream chunks, or use an appropriate engine | Peak memory includes copies/intermediates; sample design must match question |
| No usable data | Define instrumentation, sampling, annotation, and retention plan | Collection cost, representativeness, access, outcome delay, acceptance criteria |

Pandas supports many input formats, but parsing and dtype choices remain explicit project decisions. SQL reads can stream chunks; chunking alone does not make all downstream algorithms incremental. [Pandas I/O](https://pandas.pydata.org/docs/user_guide/io.html), [SQL query reader](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html), [Scaling pandas](https://pandas.pydata.org/docs/user_guide/scale.html)

### CSV tokens with domain meaning

When a dictionary names absence categories or tokens such as `None`, `NA`, `NULL`, empty strings, or zero-padded keys, compare a bounded raw-token read against the parsed frame before profiling or exporting a split. Parser defaults can silently collapse valid categories into missing values; `dtype=str` alone does not prevent this.

Choose null tokens per column from documented meanings. In pandas, `keep_default_na=False` disables the default token set; combine it with explicit `na_values` and types as needed, rather than globally declaring every token valid or every `NA` unknown. Verify category/null/key counts and representative absence/unknown rows after parsing and after any saved/reloaded extract. Apply the same input contract at training and inference. Fixed schema parsing can precede splitting; imputation statistics remain training-only. [Pandas CSV null parsing](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

If an upstream extract already collapsed distinct states, recover from the authorized raw source and create a new input version. If that source is unavailable, record the lost distinction and return to acquisition for recovery or an explicitly bounded use; an imputer or a limitation note cannot restore discarded information.


## 1.5 Basic dataframe inspection contract

Before target-guided modeling, inspect shape, dtypes, memory, null/nonfinite counts, key uniqueness, exact and semantic duplicates, category counts, time ranges, units, and impossible values. Compare column names against the dictionary. Preserve missing versus zero versus not-applicable distinctions. Inspect bounded examples with sensitive values masked.

For each join, specify intended cardinality and unmatched-row policy. Compare row and unique-key counts before and after; inspect unmatched keys and unexpected duplication. Use `validate` and `indicator` where suitable: a many-to-many merge may multiply observations without any parser error. Pandas also matches null join keys to each other, unlike typical SQL null semantics, so inspect null keys explicitly. [Pandas merging](https://pandas.pydata.org/docs/user_guide/merging.html)

Historical features require an as-of contract. Distinguish event time, ingestion/availability time, correction time, prediction time, and label time. A lab result recorded for Monday but received Wednesday was unavailable to a Tuesday decision. Point-in-time joins help retrieve historical values, but the source must retain the timestamps needed to represent actual availability. [Feast point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins)

Structural inspection can precede a split. Once evaluation is defined, estimate transformations, select features, and perform target-guided exploratory decisions using training data. Keep the final test set for the stated evaluation; test-informed decisions invalidate its role. [Leakage and pipelines](https://scikit-learn.org/stable/common_pitfalls.html)


## 1.6 Collection and annotation decisions

Specify who/what is sampled, inclusion/exclusion, time windows, strata, rare-event enrichment, logging failures, and nonresponse. If sampling changes prevalence, retain sampling probabilities or enough information to evaluate under the intended population. Acquire examples that fill a measured coverage gap, not merely those easiest to obtain.

For labels, define the event and horizon, annotation rubric, ambiguous-case policy, annotator training, independent review subset, disagreement resolution, and versioning. Agreement measures alone do not establish validity: annotators can agree on a flawed rubric. Distinguish weak labels, model-generated pseudo-labels, and verified outcomes. Maintain a genuine evaluation set independent of labeling shortcuts used in training.

When consent, licensing, access, or intended use is unresolved, describe the needed source and decision rather than collecting indiscriminately. Record provenance, collection context, and known limitations so later users can assess suitability. [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)


## Exit gate and return paths

### Resolve acquisition ambiguities before they become modeling assumptions

| Finding | Decision and next action |
|---|---|
| Several tables could define one observation | Specify the base entity/event table, prediction-time index, join keys, aggregation windows, and expected row count before merging; preserve a row lineage back to sources. |
| Repeated entity IDs or identical-looking rows | Determine whether these are ingestion duplicates, repeated real events, or repeated measurements. Deduplicate only confirmed duplicate observations; preserve legitimate events and use appropriate grouping/weighting. |
| Only a convenience sample is accessible | Keep it as a development sample, document selection, and seek target-population evaluation. Weighting cannot recover a population segment with no observed support. |
| Historical labels and current source values disagree | Version the correction and identify affected cohorts. Reconstruct availability at prediction time; if historical snapshots do not exist, bound the claim rather than presenting today's extract as historical truth. |
| Multiple candidate datasets have incompatible units or label definitions | Reconcile semantics or model/evaluate separately. A common column name is insufficient evidence to concatenate datasets. |
| Acquisition would outlast the decision horizon or exceed budget | Compare a simpler observable target, a smaller supported population, a human/rule-based process, or stopping. Record what future evidence would change that decision. |

These are workflow decisions from the source/provenance checks above. The resulting population, key, and timing definitions feed [label/split design](../../evaluation/references/labels-splits.md); sampling and event multiplicity also feed [metric aggregation](../../evaluation/references/metrics-policy.md#27-aggregation-and-incomplete-targets).

Proceed when the action and baseline are defined, a reproducible data source is available, feature/label timing is understood where applicable, and an evidence design appropriate to the task is feasible. An unlabeled descriptive or clustering task does not require inventing a supervised label. Otherwise produce a specific acquisition or non-ML plan with owner, cost, acceptance criteria, and re-entry condition. Changes to population, action, outcome, or data availability reopen framing and downstream evaluation.
