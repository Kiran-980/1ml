# Security policy

## Report a vulnerability privately

Use [GitHub's private vulnerability reporting form](https://github.com/Kiran-980/1ml/security/advisories/new).
Include the affected version, a minimal reproduction, expected impact and any
mitigation you have tried. Use synthetic examples and redact credentials and data.
If the form is unavailable, open an issue asking for a private reporting channel
without including vulnerability details.

Security fixes target the latest release on `main`; older releases may need an
upgrade. Reports are reviewed by the maintainer without a guaranteed response SLA.

## Trust boundaries

1ml supplies agent instructions and Python helpers. Instructions do not provide an
operating-system sandbox or guarantee safe model behavior. Review generated code
and grant only the data, filesystem and account permissions needed for your task.
Do not give an untrusted notebook credentials or run it in a privileged environment.

The public repository's CI does not need Kaggle credentials or production secrets.
Fork pull requests use read-only permissions. Maintainer account automation and its
credentials are kept separately. Report any apparent secret exposure privately;
do not copy the secret into an issue or attempt to use it.
