# clustering

## Clustering

**Documented:** Algorithms encode different geometry and assignment capabilities: k-means favors compact Euclidean clusters; density methods can represent nonconvex structure and noise. ARI/AMI compare partitions when reference labels exist. Silhouette favors separated convex clusters and can misjudge density-based solutions. [scikit-learn clustering](https://scikit-learn.org/stable/modules/clustering.html)

**Decision synthesis:** Define why grouping is useful and the meaningful similarity measure first. Compare k-means/mixtures for compact or probabilistic segments, density methods for noise/nonconvex structure, and hierarchical methods when nested groupings matter. Check sensitivity to scaling, representation, resampling and hyperparameters. Inspect segment sizes, stability and whether proposed actions differ usefully between segments. Do not manufacture 'true' classes from cluster labels or choose k only from an elbow. Explain how a new record gets assigned; some algorithms are transductive and need an explicit assignment policy. If no stable/useful structure appears, record that result rather than forcing segmentation.
