# Agent installation

Keep the complete repository together. Skills refer to sibling skills and shared `references/`, `rules/`, and `tools/` using relative paths. Copying individual skill folders through a generic installer can break those links. Host packaging below points to the same twelve skill bodies; it does not flatten them into one prompt.

This repository is public. Cloning it does not require repository access credentials, although an agent host may still require its own account or authentication. If a host's remote installer is unavailable, clone first and use its local installation/configuration route. Never embed access tokens in repository URLs or configuration examples. This repository's catalog is not a curated marketplace listing.

Codex and Claude native installation/discovery were verified on 2026-10-28; see [verification](#verified-installation). The other routes are documented integration paths, not end-to-end certifications. Fresh Astra trials used explicit skill-file access. See the README's verification boundaries.

## Clone the repository

The successful Codex and Claude installs recorded below used existing HTTPS Git authentication while the repository was private. Public installation no longer requires that access. Contributing changes still requires the appropriate GitHub permissions; do not paste tokens into commands or skill files.

For local-install routes, clone the complete repository once into a stable location:

```sh
git clone --branch main https://github.com/Kiran-980/1ml.git /absolute/path/to/1ml
```

Replace the placeholder with your chosen directory, such as `D:/plugins/1ml` on Windows. Keep source data and learner projects outside the installed plugin. No model-provider credentials are required merely to install these instructions.

## Claude Code

```text
/plugin marketplace add Kiran-980/1ml#main
/plugin install 1ml@1ml
/1ml:lifecycle
```

For a local checkout: `claude --plugin-dir /absolute/path/to/1ml`. This repository includes its own catalog; it is not an Anthropic-curated listing. [Official marketplace instructions](https://code.claude.com/docs/en/plugin-marketplaces).

The equivalent terminal commands, used for the verified user installation, are:

```sh
claude plugin marketplace add Kiran-980/1ml#main
claude plugin install 1ml@1ml --scope user
claude plugin details 1ml@1ml
```

Expect `Skills (12)`. Open a new Claude session and invoke `/1ml:lifecycle`. For updates, run `claude plugin marketplace update 1ml` followed by `claude plugin update 1ml@1ml`. FCC launches Claude Code and normally shares this user plugin profile; a custom `CLAUDE_CONFIG_DIR` is a separate profile.

## Codex

Use the native plugin CLI (verified with Codex CLI 0.162.1):

```sh
codex plugin marketplace add Kiran-980/1ml --ref main
codex plugin add 1ml@1ml
codex plugin list --marketplace 1ml --json
```

The last command should show `installed: true` and `enabled: true`. The installed client accepts this repository's marketplace catalog and uses `.codex-plugin/plugin.json` to discover `./skills/`. Start a fresh session, use the skill picker to select `1ml:lifecycle`, or explicitly ask Codex to use that skill. If an already-open desktop app retains its previous inventory, restart it; do not create duplicate standalone skill copies.

Refresh the source with `codex plugin marketplace upgrade 1ml`, then run `codex plugin add 1ml@1ml` to install the selected catalog version. These commands are version-dependent; check `codex plugin --help` on older clients.

For a local development checkout, `codex plugin marketplace add /absolute/path/to/1ml` registers its catalog. As a fallback for clients using local marketplace files, merge this entry into your project's `.agents/plugins/marketplace.json`, with the checkout at `plugins/1ml` relative to the project root:

```json
{
  "name": "local-ml",
  "plugins": [{
    "name": "1ml",
    "source": {"source": "local", "path": "./plugins/1ml"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
  }]
}
```

Restart the client and enable the local plugin. Preserve other marketplace entries. This manifest does not register a public directory listing. [Official packaging and local installation](https://developers.openai.com/plugins/build/plugins).

## Automatic updates

1ml uses the host's plugin manager to download releases from this repository. Install using the explicit `main` references below. `develop` is the contribution default; `main` is the stable release source. Local development checkouts follow their own update workflow.

**Claude Code:** open `/plugin`, select **Marketplaces → 1ml → Enable auto-update**. Third-party marketplaces default to auto-update off. Once enabled, Claude checks and installs updates in the background after a session starts. Run `/reload-plugins` or start a new session to load the downloaded version. [Claude's automatic update behavior](https://code.claude.com/docs/en/discover-plugins#update-plugins).

**Codex:** native Git marketplace registrations are refreshed by the startup background updater when plugins are enabled. Codex then refreshes installed packages from those sources; no separate 1ml updater setting is needed. This behavior is present in [Codex 0.162.1's plugin manager](https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/core-plugins/src/manager.rs). Allow the startup refresh to finish and start a fresh chat to use the new skill instructions. Restart an already-open desktop app if its inventory remains stale.

Updates require network access and a running host; they do not hot-swap instructions already loaded in a conversation. To request an update immediately:

```sh
# Claude Code
claude plugin marketplace update 1ml
claude plugin update 1ml@1ml

# Codex
codex plugin marketplace upgrade 1ml
codex plugin add 1ml@1ml
```

For each release, maintainers must bump the same version in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, and `package.json`, run the package checks, then merge the tested release PR from `develop` into `main`. A version bump lets host caches recognize the new package. Automatic updates follow published commits; users receive them on a later successful host refresh.

## Gemini CLI

```sh
gemini extensions install https://github.com/Kiran-980/1ml --ref main
```

The extension manifest exposes the root `skills/` directory. Check `gemini extensions list`, restart the session, and ask Gemini to use the `lifecycle` skill. Update with `gemini extensions update 1ml`. For an authenticated local clone, use `gemini extensions link /absolute/path/to/1ml`. Avoid separately installing the same skills twice. [Official extension format](https://geminicli.com/docs/extensions/reference/) and [skills](https://geminicli.com/docs/cli/skills/).

## OpenCode

Clone the repository to a stable location. Merge an absolute path to its `skills` directory into your existing `opencode.json` or `opencode.jsonc` configuration, preserving other entries:

```json
{"skills": ["/absolute/path/to/1ml/skills"]}
```

On Windows use a path such as `D:/plugins/1ml/skills`. Ask the agent to load `lifecycle`. This is a skill collection, not an OpenCode JavaScript plugin. Current schema accepts the array form; older releases may require `{"skills":{"paths":["/absolute/path/to/1ml/skills"]}}`. [Official configuration schema](https://opencode.ai/config.json) and [skill discovery](https://opencode.ai/docs/skills/).

Update the clone with `git -C /absolute/path/to/1ml pull --ff-only`, then start a fresh session. Keep the whole checkout in place so shared references remain reachable.

## Pi

```sh
pi install git:github.com/Kiran-980/1ml@main
```

Invoke `/skill:lifecycle`. The `pi.skills` entry in `package.json` selects the existing skills directory. No npm publication or JavaScript extension is required; `private: true` prevents accidental npm publication, not Git installation. [Official Pi packages](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/packages.md).

Check the package with `pi list`. An authenticated local clone can be installed with `pi install /absolute/path/to/1ml`, or tried without saving installation using `pi -e /absolute/path/to/1ml`. After pulling a local clone, use `/reload` or start a new session. For managed Git packages, consult `pi update --help` for your client's update syntax.

## Hermes

Clone the repository and merge its absolute skills path into `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/1ml/skills
```

Check `hermes skills list`, then request `lifecycle`. External directories can be modified by the agent when writable; use a dedicated checkout if you also maintain the source. [Official Hermes skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

Update the clone with `git -C /absolute/path/to/1ml pull --ff-only` and start a fresh session. This is Hermes's native external-skills route. Unlike Superpowers, 1ml does not currently ship a Hermes Python plugin/bootstrap adapter, so do not use `hermes plugins install` for this package.

## Verify installation

Confirm twelve skills are discoverable. Ask the agent to read `lifecycle`, then open its linked framing and notebook-protocol references. Confirm paths resolve inside the same checkout. Start with a small synthetic task before granting access to real data. Installation/discovery success is separate from scientific correctness and executable notebook quality.

Any file-capable agent can also read `/absolute/path/to/1ml/skills/lifecycle/SKILL.md` directly and follow its linked owners. That fallback is explicit use, not automatic native skill discovery.

### Verified installation

On 2026-10-28, version **0.2.0** was installed directly from the private repository in both user profiles:

| Check | Codex CLI 0.162.1 | Claude Code 2.1.310 |
|---|---|---|
| Private Git marketplace registration | Passed | Passed |
| Native installed plugin | Enabled | User scope |
| Native skill discovery | 12 enabled entries from app-server `skills/list` | `plugin details` lists 12 skills |
| Installed package references | 46 Markdown files, 194 local links, zero errors | 46 Markdown files, 194 local links, zero errors |

Expected names: `data`, `evaluation`, `experiment`, `explore`, `frame`, `lifecycle`, `operate`, `prepare`, `release`, `statistics`, `train`, `validate`. Plugin hosts namespace these as `1ml:<name>` where supported. Each body and linked reference remains a separate file.

Validation ran against the actual installed cache directories, not just the development checkout. All installed skills and reachable local reference targets were opened successfully and compared with the source commit. This was a deterministic installation/discovery check without model inference; it does not claim every skill was behaviorally exercised in a new conversation or that the already-open desktop sidebar refreshed.

## Packaging approach

The [Superpowers README](https://github.com/obra/superpowers) is a useful example of documenting installation per host. 1ml likewise keeps one canonical skill tree and small host manifests. Superpowers also includes workflow bootstrap hooks/adapters; these are specific to that project and are not a prerequisite for 1ml's selective skill loading. Other agents can use the explicit file-loading fallback until their native integration is documented and verified.

## Marketplace distribution

A public repository is a distribution source, not an automatic curated listing. Claude users can add this repository's catalog immediately. Other directories have their own submission/review or indexing mechanisms. No curated marketplace submission is included in this release.
