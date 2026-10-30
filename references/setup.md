# Runtime setup and helper use

The plugin supplies agent instructions and local Python helpers. Use the learner project's chosen Python environment; inspect installed packages before installing anything. Core helpers need Python 3.10+ and the packages in [requirements.txt](../requirements.txt). Model training uses task-specific libraries chosen for the project; check their installed-version documentation and record the environment. No startup hook installs packages or reads datasets automatically.

## Notebook dependencies

Resolve the learner project before running pip, reading data, importing local modules or writing results. The current notebook, requirements and custom source files should form a runnable project at its delivered location; a harness-provided working directory is not a dependency solution. Use an explicit project-root setting or a bounded, unambiguous project-marker lookup when kernels may start elsewhere. Verify the requirements file exists, print the selected project/requirements path and active interpreter, and resolve file operations consistently from that root. Stop with an actionable path error when the project is ambiguous instead of searching arbitrary directories or installing an unrelated requirements file.

Create runtime/cache and output directories in setup, including missing parents. A folder precreated by an authoring helper is not a shipped dependency. Verify a standalone project containing the declared notebook, inputs, requirements and custom modules, without the authoring harness, cell plans, caches or environment. Any required generated directory must be recreated by the notebook rather than requiring the user to copy evaluator scaffolding.

Include an executable pip setup cell before third-party imports in a runnable notebook. Choose the dependencies actually used by this task; plugin helper dependencies are not automatically the analysis dependencies. Use `%pip install ...` in IPython or `subprocess.check_call([sys.executable, '-m', 'pip', 'install', ...])` so installation targets the active kernel. Pass package arguments as a list, not a shell-built command. A nonzero install result must stop execution. A dependency comment or `pip freeze` output alone does not install anything.

Create or update the learner project's `requirements.txt` with its direct analysis dependencies and compatible versions before the setup cell runs; install from its resolved path. When analysis adds a package, update the file and setup together, then verify in a clean kernel. Do not overwrite unrelated existing requirements or mistake an already installed package for a declared dependency. Record the Python version and actual resolved package versions separately. Preserve pip's stdout/stderr on failure so a missing file, missing pip, incompatible version or network failure can be distinguished; a bare `CalledProcessError` is insufficient diagnosis.

Prefer a project virtual environment and documented compatible versions. Reuse satisfied dependencies; avoid unconditional upgrades, global `--user` installs, or changing unrelated environments. Install before importing a package; if an already-imported dependency changes, restart the kernel and rerun cleanly. Save the requirements specification and actual installed versions with the artifacts. An offline or restricted environment may require a configured cache/index or owner action; report that boundary rather than silently skipping setup or disabling verification.

IPython documents `%pip` as installing into the current kernel: [pip magic](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-pip).

## Helper paths

When authoring JSON, Markdown or code on Windows, use explicit UTF-8 reads and writes. Windows PowerShell's default `Get-Content` decoding can turn valid UTF-8 punctuation into corrupted text; use `Get-Content -Encoding UTF8` or Python `read_text(encoding='utf-8')`. Check the saved notebook text and rendered labels after shell-based round trips, not only whether the JSON parses or code executes. Repair encoding in the source plan and regenerate affected text/figures; never apply blind substitutions to legitimate non-English content.

Resolve paths from the installed plugin, not the current working directory. Shell examples use placeholders: substitute actual absolute paths and quote them using the active shell. The plugin cache may be read-only; outputs and environment files belong to the learner project.

```text
python <plugin>/tools/data_profile.py --csv <source.csv> --max-rows 1000 --out <project>/1ml/artifacts/profile.json
python <plugin>/tools/data_profile.py --sqlite <source.db> --table observations --max-rows 1000 --out <project>/1ml/artifacts/profile.json
python <plugin>/tools/state.py show --project <project> --summary
python <plugin>/tools/render.py --plan <cell-plan.json> --notebook <notebook.ipynb> --project <project> --stage data
```

The profiler produces descriptive facts plus heuristic kind/target guesses. A name-based target guess is not confirmation of the business outcome. CSV/SQLite row limits provide an initial slice, not representative sampling. Confirm file/schema/units and observation timing separately. Parquet requires a compatible engine and an explicit loading strategy for large files; do not assume row-limiting CSV behavior applies to every format.

Do not echo sensitive profile content into chat by default; inspect compact counts and redacted examples appropriate to the source. Artifact files inherit the learner project's access controls. Avoid loading more records than the task/resource budget justifies.

The YAML matcher provides prompts for investigation, not automatic imputer/model/metric choices. Read the matched reference and inspect evidence before acting. Current [capabilities](capabilities.md) distinguish implemented helpers from task-specific analysis code the agent must write and verify.
