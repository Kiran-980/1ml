# ranking

## Ranking and recommendation

**Documented:** Learning-to-rank uses relevance judgments grouped by query. XGBoost requires group information; ranking scores are relative relevance scores. NDCG permits graded relevance, whereas MAP is for binary relevance. Clicks can contain position bias and noise. [XGBoost learning to rank](https://xgboost.readthedocs.io/en/stable/tutorials/learning_to_rank.html)

**Decision synthesis:** Define the candidate universe, query/session unit, relevance label, and displayed cutoff. Keep query groups intact in validation; use chronological evaluation if future interactions are the deployment target. Choose NDCG@k, recall@k, precision@k, or reciprocal-rank measures according to the user task; report the candidate sampling protocol because changing negatives changes the problem. Assess new-user/new-item cohorts separately. Do not equate unobserved items with known dislikes or ranker scores with calibrated probabilities.

**Documented:** Retrieval selects a tractable candidate set from a potentially huge catalogue, then ranking selects a shortlist. Two-tower retrieval represents query and candidate separately; serving can use an approximate-nearest-neighbour index. [TensorFlow Recommenders retrieval](https://www.tensorflow.org/recommenders/examples/basic_retrieval)

**Decision synthesis:** Begin with popularity/recency or content heuristics; compare collaborative/content/hybrid models where interaction coverage allows. Track retrieval recall before blaming the ranker; measure the combined pipeline, index freshness, exclusions, diversity and business value. Historical feedback is policy-shaped: offline improvement should be followed by controlled online evaluation when feasible, with safe rollout and guardrails.
