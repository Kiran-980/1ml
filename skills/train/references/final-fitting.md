# final fitting

## Artifact portability

Keep one implementation of preprocessing and inference. If custom code is needed, put it in an importable module beside the project artifacts, import it in every notebook stage, and record its path and environment requirements. Built-in pipelines need no custom module merely to satisfy a template. Save the fitted preprocessing and estimator together.

In a fresh interpreter with the recorded dependencies, load that bundle without executing training or notebook definition cells. Supply the same raw feature schema used for fitting; verify prediction values, row order and, when used, probabilities against saved outputs. Assert parity with an appropriate tolerance. A notebook-only definition, class redefinition, missing source module or different representation is a packaging failure, not evidence of poor model quality. Repair that boundary before final scoring. Treat model pickle/joblib files as executable artifacts and load only trusted project outputs.

Environment compatibility and limitations of custom Python components are described in [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html).

## 6.9 Choose and hand off the complete procedure

Compare metric uncertainty, operational constraints, robustness, and maintenance cost. Document why the chosen candidate wins over the baseline and why alternatives lose. If evidence is inconclusive, preserve that result and specify the next useful measurement rather than declaring a winner from decimal differences.

Hand off the preprocessing/model/policy bundle, fitted artifacts, selection protocol, validation predictions, limitations, and unresolved release risks to [system validation](../../validate/references/system-evidence.md). Specialized task branches in [chapter 7](../../../references/tasks/index.md) override generic supervised assumptions where needed.


## 6.10 Refitting, calibration, and policy order

Make the final fitting procedure explicit before consulting final evaluation. A simple design, when data support it, is: choose the base pipeline using development-only selection; fit it on its designated training data; fit any calibrator on disjoint base-model predictions; choose a threshold/policy on a suitable development validation role if it must be optimized; evaluate the frozen complete bundle on the final test. A threshold derived from agreed fixed costs does not itself require a threshold search. Calibration and thresholding are optional when the task does not need them.

These are **roles**, not a requirement to carve every dataset into five tiny pieces. Valid cross-fitting or nested procedures can use data more efficiently, but every learned step must respect its fitting boundary. Already fitted classifiers require disjoint calibration data; supported cross-validated calibrators can generate out-of-fold scores and combine/refit according to their documented design. Inspect ensemble/refit behavior and the internal splitter rather than treating all calibration APIs as equivalent. [CalibratedClassifierCV](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)

If the same development data are used to choose calibration method and threshold, regard that as joint selection, not independent evidence that either generalizes. Keep independent final evaluation of the whole selected policy. With inadequate data, reduce the number of fitted choices, use a valid simpler procedure, or limit the probability/policy claim; see [split infeasibility](../../evaluation/references/inner-validation.md#36-when-a-valid-split-is-not-feasible).

Changing/refitting the base model can change its score distribution. Rebuild or validate downstream calibration, thresholds, and interval construction as part of the specified refit procedure; do not attach an old calibrator to new weights without evidence. Standard split-conformal calibration also relies on a base fit independent of its calibration outcomes; refitting on that calibration data changes the validity argument. [Conformal construction](https://arxiv.org/html/2107.07511v6)

Save the exact evaluated bundle and its lineage. A later all-data refit is a new artifact: distinguish evaluation of the learning procedure from measurement of that exact artifact. If an old test cohort is intentionally absorbed into training, retire its untouched-test status and plan fresh prospective/external evaluation. Never keep labeling its old score as an independent test of a model trained on those records. This protocol connects selection to [release validation](../../validate/references/system-evidence.md) and [versioned packaging](../../release/references/packaging-rollout.md).

Removing calibration or threshold search does not restore independence to a test already used to adapt the procedure. If re-evaluating a refit on the same cohort was prespecified and its results did not guide choices, describe that evidence and its dependence explicitly; otherwise obtain fresh independent evidence. Never declare test reuse valid merely because the new model is simpler. Cost-based probability thresholds require a suitable probability scale and decision assumptions; arbitrary raw scores cannot be treated as probabilities. Verify calibration APIs against the installed version before giving implementation syntax.
