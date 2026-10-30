# Evaluating 1ml

An evaluation measures a particular model, agent host, plugin snapshot, tool environment, and task distribution. A skill passing once does not certify every model or deployment. See [observed results](results-summary.md) and the broader [scenario inventory](../scenarios/decision-paths.md).

The deliverable is the plugin. Files under `tests/` are maintainer verification tools, not runtime skills or a Kaggle product. The proposed competition runner belongs in a separate project that installs a pinned plugin snapshot; datasets, submissions and raw runs stay outside the distributed plugin.

## What to measure

| Layer | Evidence | What it cannot establish |
|---|---|---|
| Package and helper tests | Links, schemas, state transitions, notebook replay, executable invariants | Agent selection or scientific judgment |
| Fresh instruction probes | Task decisions and actual resource reads with isolated context | Native host discovery, model training, production behavior |
| Host integration | Implicit/explicit skill invocation, successful tool results, artifact execution, complete trace | Generalization to every provider/model |
| End-to-end ML tasks | Valid split/pipeline, reproducible fit, hidden evaluation score, resource use | No-ML, business framing, incident, causal, or release competence by itself |

Use deterministic checks for artifact validity and measurable boundaries. Review scientific decisions against a rubric; model graders require calibration against human-reviewed examples and can be wrong. Read the trajectory and execution results, not just an articulate final response. Anthropic's [agent-evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) recommends combining grader types and layers.

## Cases and independence

The twelve `*/case.yaml` files are JSON-compatible YAML for Claude Code's native evaluator. They contain realistic prompts and separate graders. Eleven are design questions, one is an arithmetic negative control. They intentionally do not request execution. Do not give grader criteria, previous answers, suspected defects, or answer keys to the acting agent.

The prompts are implicit invocation tests under the native host. The separate Codex instruction probes explicitly select an entry skill and therefore cannot measure discovery. Add explicit-invocation native cases when diagnosing routing versus instruction-following failures.

For each native trial, start a fresh workspace/session with synthetic or approved data and only the intended plugin. Separate acting-agent files from hidden labels and evaluator files by filesystem access, not a prompt asking it not to peek. Record package file hashes, host/model/provider versions, sampling settings, tool grants, timeout/turn/compute limits, final output, execution artifacts, and the complete tool trace. With no Git repository, use a file-hash manifest rather than inventing a commit identifier.

Compare with-plugin and without-plugin arms using the same model, task, compute and context budgets. Keep scientific/artifact graders identical; plugin invocation is a diagnostic only for the plugin arm. A one-run smoke test finds obvious failures. For a baseline comparison, repeat independent trials (initially at least three per arm), report per-case results and variability, and keep unreleased cases to check that fixes generalize. Do not claim a reliable average improvement from three examples.

Reference checks should inspect successful content loads, their order and volume. Metadata discovery is distinct from loading a body. `tool_used` counts calls, so review failed reads and tool denials before interpreting its score. A list of forbidden unrelated files is only a regression guard, not proof that every other read was necessary. Count repeated loads and loaded bytes/tokens separately. Review alternate valid routes rather than prescribing an exact sequence of skill names.

## Native Claude Code / FCC runner

[Native plugin evals](https://code.claude.com/docs/en/plugin-evals) support isolated trials, baseline arms, tool-call graders, rubric graders, and local reports. The installed Claude Code 2.1.310 parsed this suite. Its first preflight stopped before inference because the sandbox user's temporary path contains braces; this is an infrastructure error, not a zero-quality skill result.

FCC is a third-party launcher/proxy for the real Claude Code host. Local inspection verified FCC 6.16.17 and its launcher. Normal Anthropic `auth status` does not describe FCC provider authentication. The managed configuration has an OpenAI fallback: pinning the NVIDIA model alone does not disable it. Our [local runner](run_fcc.py) uses the installed FCC provider, converters and launcher with an isolated NVIDIA-only configuration, no fallback credentials, no admin routes and no global configuration changes. A real agent returned `391`; native skill trials also reached the endpoint. See the [FCC repository](https://github.com/Alishahryar1/free-claude-code).

Use the Python environment containing the installed `free-claude-code` package (on this machine the uv tool environment). Each run name must be new:

```powershell
python -X utf8 tests/evals/run_fcc.py --run my-native-run --timeout 480 --cases structural-missingness unseen-sites
```

The wrapper pins both actor and judge to the same NVIDIA model and runs cases sequentially. Add `--explicit` for a separate diagnostic arm that names the entry skill; this does not prove automatic discovery. It records source/case/runner hashes and transport metadata. `--spacing-seconds 10` lowers admission to at most six requests per minute; the default is three seconds. A native API 429 stops the batch and records the remainder as not run. Credentials remain in memory and are not recorded. `--trust-plugin` acknowledges this locally authored suite; it does not grant shell writes or production operations. A rate limit/auth/transport/timeout failure must remain separate from a valid agent failure. Do not fix those by changing the skill. The initial actor/judge combination produced several scientifically incorrect automatic passes; manual review remains necessary.

Calibrate graders with known-correct and deliberately incorrect controls before using them as gates. Our exact-answer negative control correctly failed both regex and LLM grading, while long scientific answers still received false passes. That is not sufficient judge validation. Prefer executable invariants for code/data behavior and retain manual review of scientific claims; do not replace scientific correctness with keyword matches. In native design probes, tool-read checks measure coverage/compliance, not proof that a particular reference was scientifically necessary or correctly applied.

If the Windows sandbox path issue recurs, use an isolated workspace and temporary path without permission-pattern metacharacters; preserve the error and verify that the host's permission boundary still works. Do not disable permission checks to make a run green. Keep reports local with `--no-publish`. A native cost estimate may not reflect a proxy's actual billing; enforce provider and request budgets independently.

The runner sets temporary directories per process and stores outputs in ignored `tests/eval-runs/`, outside native case discovery. Preserved native sandboxes contain directory links, so putting them under `tests/evals/` makes subsequent case discovery fail. Windows native eval also warns that it cannot seal directories with chmod: read reports as untrusted data; do not run Git/config-loading commands inside preserved sandboxes. Broad reads of the empty actor workspace can be denied while authorized plugin reads work; this is distinct from a failed provider request.

Run `summarize_native.py tests/eval-runs/<run>` to collect answers and successful/failed tool results for review. It does not replace a scientific grader. Native `tool_used` checks alone can count attempted reads, and scores combining reference checks with scientific criteria are not pass probabilities.

The local test environment also denied default temporary-file writes and stalled at Jupyter kernel startup. Workspace-local temporary directories fixed the write issue; the same focused notebook test passed on the host in about eight seconds. This local workaround does not prove a root cause or repair the underlying Windows sandbox. Do not weaken notebook assertions or treat a stalled run as a passed test.

## Provider-independent option

An API supplies model responses, not an autonomous filesystem/tool loop. The loop must discover skill metadata, load the chosen body, read linked references on demand, execute authorized tools, and log their results. Pasting the entire plugin into a single API prompt does not test progressive disclosure.

[Inspect AI](https://inspect.aisi.org.uk/agents.html) is a suitable evaluation foundation: it can run its own agent or integrate external agents. Its [OpenAI-compatible provider](https://inspect.aisi.org.uk/providers.html) accepts provider-specific API key and base URL settings; its [Agent Bridge](https://inspect.aisi.org.uk/agent-bridge.html) supports external agent frameworks. Use a native Claude/FCC adapter to measure this plugin's actual host behavior, or clearly label a custom skill-loader adapter as a separate compatibility target. No Inspect adapter is implemented here yet.

NVIDIA's [API reference](https://docs.api.nvidia.com/nim/reference/llm-apis) documents `https://integrate.api.nvidia.com/v1/chat/completions`. The [configured model page](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b) currently lists a free endpoint, and the [FAQ](https://docs.api.nvidia.com/nim/docs/product) describes free prototyping access. This does not guarantee unlimited requests, account eligibility, throughput, or free compute for training competition models. The user suggested approximately 40 RPM; no account-specific quota was verified. The isolated runner admits one request per three seconds with concurrency one (at most 20 RPM), with bounded installed-provider retries. Record retry/wait time and distinguish transport errors from skill failures.

## Kaggle benchmark pipeline recommendation

Use offline competition tasks before live submissions. [MLE-bench](https://github.com/openai/mle-bench) already supplies preparation and local grading for Kaggle-derived competitions. It creates held-out data from publicly available training data and is agent-agnostic. Its published benchmark uses 75 competitions; even its 22-task lite set is substantial. Start with two or three small, curated tasks suited to available compute instead of downloading everything. Pin the benchmark version and inspect its known issues; a reduced subset is a custom smoke benchmark, not a comparable full MLE-bench score.

Proposed pipeline (not implemented):

User direction: proceed one step at a time. Finish current skill verification, then select one small classical-ML competition to prove the workflow. The eventual collection can grow toward roughly 100 balanced problems, but its current scope is classification, regression, forecasting and the [scikit-learn model-selection map](https://scikit-learn.org/stable/machine_learning_map.html), including clustering and dimensionality reduction. Generative-AI tasks are excluded for now. Curate by task, dependence/leakage challenges, missingness/imbalance, difficulty, size and compute budget. Clustering and dimensionality reduction may need local downstream/stability checks rather than a competition leaderboard. Do not select merely popular competitions or claim Kaggle covers every ML problem. Keep no-ML, inference, collection and operational scenarios outside competition scoring. Report per-category results so numerous easy tabular tasks cannot conceal a missing capability.

[KaggleHub](https://github.com/Kaggle/kagglehub#download-competition), locally verified as version 1.0.3, can download/cache competition files with `competition_download`; use the appropriate local loader for those files. Its `dataset_load` DataFrame adapters apply to Kaggle Dataset resources. The official Kaggle CLI/API supplies competition submissions and result retrieval. Record the exact file hashes, rules/access status, metric direction and leaderboard snapshot. Report raw scores and percentile/rank only where a comparable leaderboard is available; an offline holdout score is not an official Kaggle percentile. Training compute and API inference quotas are separate budgets.

Each problem owns its current notebook, requirements, modules, model, predictions and reports at its project root or descriptive child folders. `runs/<revision>/` contains notebooks only; source/dependency versions and immutable data are shared outside it. Independent evaluator evidence stays separate. New behavioral trials use an isolated project under `evals/skills/trials/`; results are local and ignored. See [current layout](../../evals/README.md). The first Titanic preparation used an older layout under `tests/eval-runs/`; preserved historical manifests describe that old run and are not the current delivery contract. Credentials belong in ignored local configuration and never in an actor workspace or model artifact.

```text
curated task registry + reviewed access/rules
  -> versioned data preparation + hidden evaluator holdout
  -> fresh sandbox per task / arm / trial
  -> fixed model endpoint + agent host + optional 1ml plugin
  -> bounded tool execution and resource-read trace
  -> submission.csv + executed notebook/code + run manifest
  -> format/invariant checks + local hidden scoring + rubric review
  -> paired comparison report
  -> separately authorized live submission, if appropriate
```

Keep hidden labels and grading secrets outside the agent container. Restrict solution/leaderboard browsing for the benchmark and record prior-task contamination risks. A model may already know historical competitions, so vary tasks and retain private synthetic cases. Do not feed final holdout or public-leaderboard results back into iterative tuning while calling them independent evaluation.

Measure valid-output rate, reproducibility, split and preprocessing correctness, metric improvement over a baseline, wall time/CPU/GPU use, API tokens/retries, and resource-loading behavior separately. Classify infrastructure failures explicitly and report them rather than dropping failed runs. An unavailable GPU is a resource constraint, not a scientific no-ML conclusion.

Keep the noncompetition scenarios: no-ML alternatives, source collection, grouped/temporal support, unknown labels, experiments, capacity, production repair, and state recovery. Kaggle usually supplies a target, metric and prepared dataset; competition score cannot evaluate those omitted business decisions.

The [official Kaggle CLI](https://github.com/Kaggle/kaggle-cli) supports data access and submissions. For each chosen competition, review its actual rules, external-data/API permissions, code-versus-file submission mechanism, runtime/internet constraints and submission limits. Do not infer one competition's permissions from another. Live submissions are a separate external integration, not required to grade offline experiments, and no submissions were made here.

## Audited fresh instruction probes

`prepare_probe.py <case-slug> <new-run-slug>` copies runtime resources into `tests/eval-runs/<run>/plugin`, writes only the user prompt, and records SHA-256 hashes. It refuses to reuse a run directory. The evaluator's rubrics, tests and ignored research are excluded.

Fresh agents read plugin files through:

```powershell
rtk proxy python -X utf8 tests/evals/read_resource.py tests/eval-runs/<run> skills/evaluation/SKILL.md
```

Paths are relative to `plugin/`; do not prefix the resource with `plugin/`. This reader records path, bytes and hash for each successful read. It rejects paths escaping the copied plugin. It is an audit instrument, not a security sandbox: an agent with unrestricted filesystem tools could bypass it. Each probe records any bypasses/tool errors in `limitations.txt`; native complete traces remain the stronger integration evidence.

Raw runs and copied packages live under ignored `tests/eval-runs/`; the concise reviewed report stays in [results-summary.md](results-summary.md). Do not distribute raw traces containing private data or credentials.
