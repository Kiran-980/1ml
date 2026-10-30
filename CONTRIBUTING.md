# Contributing to 1ml

Start a focused branch from `develop` and open your pull request against `develop`.
`main` is the stable plugin source. Maintainers release through a `develop` → `main`
pull request after all required checks pass.

## Set up and check a change

```sh
git clone --branch develop https://github.com/Kiran-980/1ml.git
cd 1ml
python -m pip install -r requirements-test.txt
python tools/validate_plugin.py
python -m unittest discover -s tests -t .
```

Use Python 3.12 for parity with CI. Keep all twelve skills and their relative
references together. Use small examples or synthetic data in tests; never commit
credentials, personal data, downloaded competition data or generated model weights.

Explain the concrete problem, resulting behavior and relevant verification in the
PR. For guidance changes, distinguish an observed agent mistake from evidence that
the instruction itself caused it. Preserve leakage checks, evaluation independence
and honest uncertainty. Avoid forcing every notebook into identical headings.

AI-assisted contributions are welcome. You remain responsible for understanding
the patch, respecting source licenses and checking factual/experimental claims.
Disclose material AI assistance and do not invent test results.

## Reviews and releases

Both long-lived branches require PRs, passing CI and resolved review conversations.
Force pushes and deletion are blocked. With one maintainer, the approval count is
zero so an author can merge their own tested PR; automated proposals remain drafts
and are never approved or merged by the learning agent.

Keep version numbers synchronized in `.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json`, `gemini-extension.json` and `package.json`. Update the
changelog, verify installation and merge the release into `main`. Tag that exact
commit with `v<version>`. Branch-based installs receive updates from `main`.

Contributions are provided under the repository's [MIT license](LICENSE). Preserve
copyright and license notices. The project remains maintained by Kiran; modified
distributions should clearly identify their changes and avoid implying endorsement.

For security issues, follow [SECURITY.md](SECURITY.md) instead of posting secrets or
exploit details in a public issue.
