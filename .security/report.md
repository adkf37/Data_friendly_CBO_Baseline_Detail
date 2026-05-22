# Security Report — Data_friendly_CBO_Baseline_Detail

## Scan Summary
- **Scanned:** 2026-05-22
- **Tools run:** pip-audit, gitleaks (unavailable), trufflehog filesystem (unavailable: installed CLI incompatible), regex secret grep fallback, bandit, semgrep --config auto (unavailable: remote config fetch blocked)
- **Status:** clean

## Remediation Notes
- `gitleaks` was not installed in the environment.
- `trufflehog filesystem .` could not be executed because the installable package provides a legacy CLI without the `filesystem` subcommand.
- `semgrep --config auto --json` could not complete because the runner could not resolve `semgrep.dev` to download the `auto` ruleset.
- Fallback regex-based secret scan found no matches in scoped file types.
