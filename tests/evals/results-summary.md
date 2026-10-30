# Observed evaluation results — 2026-10-27

Current decision: **mechanical checks pass; behavioral verification is not passed** for the tested FCC/NVIDIA configuration. All prepared initial cases and the final ten explicit retests ran. Several answers still violate scientific constraints despite reading the correct instructions. Do not treat automatic PASS votes or a tool invocation as certification for unattended competition submissions.

## FCC/NVIDIA native evaluation

The later user request authorized native NVIDIA-backed runs. A task-local adapter uses the installed FCC 6.16.17 API conversion/provider runtime and launcher with Claude Code 2.1.310. It preserves the configured NVIDIA key in memory, removes fallback routes, limits admission to one request per three seconds and one concurrent request, and leaves managed FCC configuration untouched. A real one-turn agent request returned `391` in about five seconds. Claude reports an unknown-model cost estimate; it is not evidence of NVIDIA billing.

Two infrastructure issues were reproduced and corrected: permission-pattern characters in the sandbox user's temporary path, then native case discovery rejecting directory links in preserved runs beneath `tests/evals`. Generated artifacts now live in `tests/eval-runs`, outside case discovery; temporary paths are checked for unsupported characters. Original manifests retain their original paths after relocation.

The first native missingness case automatically invoked prepare and read its reference; automatic graders passed it. Manual inspection rejected its invalid pipeline sketch (row selectors passed to ColumnTransformer; missing indicators after imputation), and a focused executable reproduction confirmed the defects. The native unseen-site case also passed automatically but its suggested narrowed-claim split contradicted the intended known-site population. These automatic passes are not accepted scientific passes.

All twelve initial native cases completed (`fcc-native-structural-01` plus `fcc-suite-02`). Five substantive cases answered without invoking any skill: refitting, production units, deterministic lookup, clustered mean, and tuning. Forecasting eventually invoked evaluation/validate but misresolved the shared task-profile path; its rubric judge also had a 120-second provider no-progress timeout. The arithmetic control correctly returned 391 without ML skills. These are separate outcomes, not a single aggregate quality percentage.

Six explicit-invocation diagnostics then completed in `fcc-explicit-01`. All invoked the requested skill; five loaded the expected methodological reference. Lookup still skipped feasibility. Operations and capacity attempted unnecessary project bookkeeping files, misresolved their paths and received tool errors. Thus explicit invocation improves access in these observations but does not establish reliable discovery or instruction following.

Manual review found automatic false passes in both modes. Examples include reused test data becoming supposedly independent after dropping calibration, output recalibration offered as a repair for a feature-unit bug, unverified zero-error/latency guarantees for a lookup, invented survey APIs and unconditional replicate-design advice, wrong A/B power/sample sizes, threshold-dependent AUROC, and customer-disjoint validation substituted for an explicitly existing-customer future claim. The native judge used the same model as the actor; its agreement is not independent evidence of correctness. `manual-review.json` and `review-input.json` retain the initial observations locally. These are parent-agent reviews, not blinded human judgments.

Evidence-supported changes clarify fold-local preprocessing and missing indicators, known-versus-unseen population claims, label observation cutoffs, shared relative paths, conditional bookkeeping reads, exact-bundle versus adaptive test reuse, survey design conditions, numerical verification, source-unit repair and threshold-versus-ranking metrics. Four entry descriptions were made more explicit about their triggers. Three scientific rubrics were strengthened without changing actor prompts.

The original implicit retest `fcc-retest-01` produced two completed answers before persistent upstream 429 failures blocked the other nine cases. Unseen-sites loaded the right references and corrected the known-hospital/new-patient split; it still needs broader independent-site evidence before a generalization claim. Structural-missingness skipped the skill and mixed structural placeholders into its suggested imputer despite prose distinguishing the populations. Its automatic scientific pass is not accepted. The nine transport failures are **not** scientific zeros. Forecasting also attempted unrelated workspace discovery before its transport failure. A later low-rate recovery canary returned 391 in about twelve seconds.

### Final explicit retest

`fcc-explicit-retest-01` completed all ten cases with ten-second configured admission spacing and one concurrent request. Transient 429s still occurred, but the installed provider recovered within its bounded retries. All ten invoked an entry skill; seven met the native case's reference-call checks. Manual review found unnecessary specialist loading in two of those seven. The exact 64 tested runtime files are preserved in `tested-source/` and match the run's source hashes.

| Case | Reviewed result | Resource finding / remaining issue |
|---|---|---|
| Structural missingness | Fail | Correct reference; imputer code contradicts claimed subgroup behavior and linear NaN handling. Executable reproduction saved |
| Immature labels | Fail | Known-customer prose improved; code still splits customers and treats sample-count parameters as durations; three unnecessary specialist profiles |
| Underpowered A/B | Partial | Core power estimate corrected to about 5%; unverified sample-size/MDE claims remain |
| Capacity overload | Partial | Correct release block and threshold route; system-evidence reference skipped, bias direction/extra calibration requirements overstated |
| Production units | Partial | Correct source repair and no calibration workaround; unobserved false-positive claims and overly broad exclusion/recovery assumptions remain |
| Refit/calibration | Fail | Correct old-score rejection; still invents D-driven selection and allows reused B/C training data to validate downstream components |
| Clustered mean | Partial | Correct joint inclusion probabilities and possible equal weights; invented Python API and variance assumptions remain; diagnostics read without clear need |
| Small-budget tuning | Fail | Preserves holdout; forces grouping and survival interpretation without target support, overstates calibration/budget claims; unrelated survival reference loaded |
| Deterministic lookup | Partial | Correct no-ML route and feasibility read; unsupported zero-error/latency guarantees and false claim that models cannot represent deterministic rules |
| Fixed-origin forecast | Partial | Core future-input leakage identified; shared profile path still misresolved, forecasting reference omitted, availability/fallback assumptions incomplete |

Seven native overall scores were 1.0, but none of these ten answers earned an unqualified manual scientific pass. Partial means useful core reasoning with material unsupported or contradictory details, not release readiness. These are single observations with explicit invocation; they do not establish automatic discovery or a causal improvement over a no-plugin baseline.

### Grader calibration

`fcc-judge-calibration-01` asked the actor for 391 and intentionally required 392 in both a regex grader and an LLM rubric. The actor returned 391; regex failed and the model voted **FAIL FAIL FAIL**, as expected. Thus the judge can reject a simple known mismatch; its scientific false passes cannot be explained merely by an always-PASS result. The exact mechanism of the domain failures is unproved. Native exit 1/score 0 is the expected outcome of this calibration control, not a broken test.

After the final behavioral run, three small reference clarifications were added: ordinary imputers/flags do not implement conditional row semantics, TimeSeriesSplit counts samples rather than calendar durations, and domain keywords do not establish specialist-task assumptions. These additions passed link/package validation but have **not** received another behavioral retest. The preserved tested snapshot predates them. Further prose-only repetition is not evidence that a model will comply; the next useful verification step is a small executed task with deterministic data/split/pipeline/output checks and human-reviewed decision evidence.

The runner now stops a batch when native report evidence contains an API 429 and records remaining cases as not run. A regression check distinguishes this condition from a scientific score of zero, a permissions error, or an answer merely mentioning rate limits. On the preserved failing reports it identifies all nine transport failures and leaves the two completed trials unclassified as transport failures. It also records case/runner hashes and supports a slower explicit request spacing.

This is a small design-probe report, not a claim that all twelve skills, executable ML work or all host behavior passed. Raw artifacts are retained locally under ignored `tests/eval-runs/`. The [evaluation guide](README.md) explains reproduction and the next benchmark layers. No 429 was observed in the initial completed native runs; the later retest did hit 429 repeatedly despite the local 20-RPM cap. The account-specific quota and cause of that limit remain unverified.

## Earlier Codex instruction-probe evidence

- Acting agents: fresh Codex collaboration agents with `fork_turns=none`, inherited default model, no model override. The tool did not return an exact model revision; no revision is asserted here.
- Each received one raw scenario prompt and an explicit entry skill in its own runtime copy. No rubric, expected answer, old response or proposed correction was supplied.
- Source is not a Git checkout. Each run has `source-manifest.json` with exact file SHA-256 hashes, `prompt.txt`, `reads.jsonl`, `answer.md`, and `limitations.txt`.
- The parent reviewed actual answers and audited successful reads against the case criteria. No paid model judge was used. These reviews are not independent blind human judgments.
- The audit reader records file content bytes, not model token counts. It does not detect bypasses through other tools. Agents reported no plugin reads outside the reader. Some initial reads had an erroneous `plugin/` prefix and were corrected; those harness errors are disclosed in each limitations file.

## Fresh-agent observations

| Case / run | Scientific outcome | Loading observation | Loaded files / bytes |
|---|---|---|---|
| Structural missingness / `probe-01` | Preserved not-applicable vs unknown; learned imputation/scaling inside training folds; conditional model pipelines | Unnecessary project-state read for design-only question | 7 / 35,707 |
| Unseen hospitals / `probe-02` | Rejected row-random CV as unseen-site evidence; identified no-positive training and undefined held-out AUC; collection route | Unnecessary project-state and notebook-protocol reads | 6 / 33,683 |
| Monday seven-day forecast / `probe-03` | Rejected future actual lags and observed weather; proposed fixed-origin backtests, valid weather vintages/fallback, relevant baselines and inventory metrics | Early forecasting profile; no unrelated specialist or bookkeeping reference | 9 / 53,349 |
| Structural missingness / `probe-01-fixed` | Same substantive safeguards retained | No state/notebook references; relevant missingness, representation and evaluation detail | 6 / 31,482 |
| Unseen hospitals / `probe-02-fixed` | Same support limitation and collection/narrowing route | No state/notebook references; inner validation, labels/splits and metrics | 4 / 26,028 |

The observed defect was conditional-loading guidance, not a scientific failure: task skills linked project-record procedures without clearly limiting them to artifact work. The smallest fix added that condition to `prepare` and `evaluation`. Two fresh agents received the unchanged scenario prompts and revised skill copies, without seeing previous runs or the reason for retesting. Both preserved the intended scientific decision while omitting bookkeeping references. This is one before/after observation per case, not a statistical claim of reliable improvement.

Recorded skill SHA-256:

| File | Before | After |
|---|---|---|
| `skills/prepare/SKILL.md` | `6233d40f47990faee3dbd706683d29c64fbaf3aae13c637143b85fe91b561788` | `2970a24cbdc9ea650cde83447ee129edf0a288d6d57dba8917a641c74528ffb6` |
| `skills/evaluation/SKILL.md` | `d32e5adcfca9d079960a0af2be989b4ae39965b2dc6afb22f8d72b316eaf907b` | `d372004e3c518551aeb44b48e63048fb2b694c19cb21ff26c59a2e34d77e51fc` |

These earlier runs exercised explicit loading. They do not demonstrate automatic Skill discovery, filesystem security, measured model quality, actual training, repeated-run reliability, or superiority over a no-plugin baseline. At that stage nine native cases had not run; the FCC follow-up above supersedes that coverage status. Data-only inspection, notebook interruption/recovery, specialist escalation and full execution scenarios remain additional behavioral coverage work from the broader inventory.

## Historical native host preflight, before NVIDIA authorization

Observed: `claude --version` and `fcc-claude --version` both report Claude Code 2.1.310. FCC package version is 6.16.17. The ordinary Claude authentication check returned no login; this is not an FCC-provider authentication test. FCC's default model is `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b`, with no role overrides and one fallback. No keys were printed and no provider settings were changed. FCC's launcher initially failed to acquire its settings lock inside the sandbox; the permitted outside-sandbox version check succeeded.

Exact native preflight:

```powershell
rtk proxy claude plugin eval . --eval-dir tests/evals --case structural-missingness --runs 1 --ablation none --no-publish --trust-plugin --max-cost-usd 2 --output-dir tests/evals/results/claude-preflight
```

The suite parsed and identified 1ml 0.2.0. The run stopped before inference with a permission-rule parser error: the Windows sandbox user's directory name contains `{}`. `aggregate-result.json` records zero turns, no grader results, and $0 reported cost. Classify this as **infrastructure failure**, not the skill score of zero shown in the generic report. Do not include it in a scientific pass-rate denominator. The local report and exact error remain in `results/claude-preflight/`.

At that historical stage, FCC/NVIDIA inference was unverified. The authorized follow-up above now verifies responses and native traces. A later user request authorized competition preparation: Titanic's metadata/pages and three CSV files were downloaded into its own ignored folder, with hashes and row/schema checks. No training benchmark or Kaggle submission has run; the larger pipeline remains a proposal, not implemented plugin functionality.

## Earlier mechanical validation

Latest complete code verification: **52 tests passed in 13.167 seconds** on the host, including the new transport classification regression and a clean-kernel synthetic notebook. The focused notebook check passed in 7.851 seconds after a sandbox run stalled for 177 seconds at startup with no child process visible; exact root cause is unproved. Default sandbox temporary-file permissions also failed, so verification uses process-local workspace temporary paths. Full output is under `fcc-explicit-retest-01/`; stall evidence remains under `fcc-retest-01/`. After the final Markdown clarifications, plugin validation still reports 12 skills, 46 runtime Markdown files and 179 local links, with no errors. Local `.env` files and generated competition/eval runs are excluded from the package copy check.

Four focused evaluation-harness tests passed: exact read-byte audit, path escape rejection, reusable case input structure, and escaping run-name rejection. The complete suite then passed **49 tests in 34.237 seconds**, including synthetic notebook execution in a clean kernel and installed-copy checks excluding local evaluation outputs. Windows Jupyter emitted platform event-loop/TCP warnings; execution completed.

Plugin validation passed for 12 skills, 46 runtime Markdown files, and 179 local links. Both edited skills passed skill-creator validation. The evaluation guide and report have no broken local links. These mechanical results are separate from the behavioral findings above.
