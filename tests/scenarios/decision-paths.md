# Behavioral evaluation cases

Run these in a fresh isolated learner project with the installed plugin, recording skill/reference reads, generated artifacts, calculations, and unsupported claims. Evaluate the behavior, not exact wording. This file specifies checks; it is not a claim that an independent agent has passed them. See the [evaluation guide](../evals/README.md) for reusable cases and the [observed results](../evals/results-summary.md) for the three scenarios actually probed so far.

| Request and fixture | Expected route/evidence | Failure to reject |
|---|---|---|
| Inspect a CSV only; no modeling request | data; bounded profile and semantics; no unsolicited training | Starts the full lifecycle or guesses confirmed target from column name |
| Small table with 80% structurally not-applicable income | prepare missingness; inspect meaning/availability; native support or justified comparison | Automatically replaces with median/mode or forces user approval from percentage alone |
| Future transactions, repeated customers, immature fraud labels | evaluation labels/splits; chronological availability, group novelty claim, maturity mask | Random split leaks future observations; unknowns become negatives |
| All positive events occur at one of three sites; goal is unseen sites | evaluation inner-validation; explicit support limitation and acquisition/narrowing route | Removes group boundary to make AUC computable |
| Daily data; Monday order covers seven days | forecasting before prepare/train; fixed-origin horizon backtest | Uses Tuesday actual demand to produce Monday's later-horizon predictions |
| Describe a population mean with clustered sampling | statistics inference; correct estimand/dependence/interval | Invents classification target or mandatory train/test split |
| Target encoding or stacking with grouped data | evaluation inner-validation then prepare/train | Uses internal random folds despite grouped outer design |
| Tune with Optuna and tiny validation support | train search-diagnosis; baseline, bounded objective, failure logs and independent evidence | Declares best trial production-ready or improves by reading final test |
| Refit after calibration/threshold selection | train final-fitting then validate; changed-score lineage and renewed policy evidence | Reuses stale calibrator/threshold and old test score as exact new-bundle evidence |
| Insufficient traffic for proposed A/B effect | experiment design/power; honest inconclusive or revised design | Treats non-significance as no effect, or starts live exposure without authorization |
| Input unit changes in production; no mature labels | operate then data/source repair; replay/fallback evidence | Retrains immediately or equates drift with concept change |
| Frozen quality passes but review queue overloads | validate/release policy-capacity boundary | Releases on average metric while dropping failed/abstained requests |
| Deterministic lookup fully solves the action | frame; documented ordinary-software/no-ML endpoint | Forces training because the plugin is about ML |
| Complex causal or censored task unsupported by installed tools | early task profile; specific research/design prerequisite | Substitutes a generic classifier and claims the specialist estimand |
| Resume after split changed and notebook write interrupted | state dependency invalidation; inspect artifact identity and replay same plan | Marks old fits current or duplicates/overwrites user cells |
| Edit an executed retail forecasting notebook with repeated stage introductions, findings tables and prior holdout exposure; preserve code/results | Consolidate repeated prose around actual questions and outputs; keep forecast origin, gap semantics, selection rule and test-exposure disclosure visible; link detailed coverage | Merely renames every stage; adds a new template around each cell; hides contamination or claims new independent evidence |
| Create a small classifier notebook and a forecasting notebook for a learner who wants a lifecycle roadmap | Task-specific organization and depth; readable outputs with consequential interpretation; complete coverage in state/report/appendix | Identical section skeletons regardless of task, forced Markdown quotas, filler deployment sections, or terse unexplained consequential decisions |
| Explain an unfamiliar threshold tradeoff to a beginner after a compact classifier comparison | Expand the explanation and use measured counts where needed; preserve small-support limits | Treats concise writing as a ban on useful teaching, removes denominators, or invents personal discoveries |

For each case record the current host/model/version, request, raw fixture, observed path, artifacts, findings, and pass/fail reasons. Context-loading evidence should show relevant branch reads and omissions of unrelated branches. Source/link validity alone cannot establish the agent followed a decision path.
