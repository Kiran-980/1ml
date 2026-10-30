# scarce labels

## Few labels: semi-supervised and active learning

**Documented:** Semi-supervised learning combines labeled and unlabeled data under distributional assumptions. Self-training uses predicted probabilities to add pseudo-labels; calibration matters. Label propagation uses a similarity graph whose construction affects memory and validity. [scikit-learn semi-supervised learning](https://scikit-learn.org/stable/modules/semi_supervised.html)

**Decision synthesis:** First benchmark labeled-only learning. Use unlabeled data only when its population and representation plausibly support the assumptions. Retain a genuinely labeled holdout untouched by pseudo-label selection; distinguish inductive deployment from a deliberate transductive experiment. Monitor errors by pseudo-label round and class. If unseen classes or severe distribution shift exist, avoid confident automatic propagation and acquire labels.

**Documented:** Active learning chooses cases for an oracle to label. Uncertainty sampling, committee approaches and density-aware strategies make different tradeoffs; noisy oracles, variable labeling costs and stopping criteria matter. [Settles's original active-learning survey](https://burrsettles.com/pub/settles.activelearning.pdf)

**Decision synthesis:** When expert labeling is available, compare active acquisition with random acquisition at equal annotation cost. Include representative exploration so a model does not repeatedly query only its current boundary. Audit annotation quality, keep the evaluation set separate from queried training examples, and stop against an agreed marginal benefit/cost criterion rather than a fixed label count.

### Positive-only labels are a distinct observation process

When confirmed positives coexist with an unlabeled mixture, ordinary supervised binary learning and ordinary 'few labels of both classes' semi-supervision are not interchangeable. Acquire representative verified labels where feasible. Positive-unlabeled methods are a specialist alternative when their labeling/selection assumptions are defensible; the classic Elkan-Noto result assumes labeled positives are randomly selected from positives. Review-selected fraud labels may violate that assumption. Preserve the observation process and an appropriate evaluation design rather than relabeling the mixture negative. [Original positive-unlabeled research](https://cseweb.ucsd.edu/~elkan/posonly.pdf)

If the assumption cannot be justified and no representative evaluation labels exist, produce an annotation/design plan or a limited review pilot. Return to [collection](../../skills/data/references/acquisition.md) and [incomplete-target scoring](../../skills/evaluation/references/metrics-policy.md#27-aggregation-and-incomplete-targets).
