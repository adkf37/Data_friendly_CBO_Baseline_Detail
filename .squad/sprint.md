# Sprint Plan - Data_friendly_CBO_Baseline_Detail

Current lifecycle target: move from **Squad Review** to **Build** with one explicit, ordered execution plan.

**Sprint status: ALL TASKS COMPLETE (Human Blocked on network for full pipeline run)**

## Ordered Build Queue

| Order | Task | Owner | Reviewers / Parallel Support | Depends On | Status | Deliverables |
|---|---|---|---|---|---|---|
| 1 | `task-01-download` | Data Engineer | Tester | None | ✅ COMPLETE | `src/download.py`, `data/raw/manifest.json`, 230 workbooks |
| 2 | `task-02-inspect` | Data Engineer | Lead, Tester | `task-01-download` | ✅ COMPLETE | `src/inspect.py`, `docs/inspection_report.md` (335 sheets profiled) |
| 3 | `task-02b-parse-plan` | Lead | Data Engineer, Tester | `task-02-inspect` | ✅ COMPLETE | `config/workbook_parse_plan.yaml` (230 workbooks, 335 sheets, 299 included) |
| 4 | `task-03-transform` — health slice | Data Engineer | Lead, Tester | `task-02b-parse-plan` | ✅ COMPLETE | 38 datasets / 13,376 rows |
| 5 | `task-03-transform` — income security slice | Data Engineer | Lead, Tester | health slice | ✅ COMPLETE | 88 datasets / 19,961 rows |
| 6 | `task-03-transform` — remaining programs slice | Data Engineer | Lead, Tester | income security slice | ✅ COMPLETE | 96 datasets / 16,742 rows · total 222 CSVs / 50,079 rows / 0 errors / 9 unit values |
| 7 | `task-04-schema` | Data Engineer | Scribe | `task-03-transform` | ✅ COMPLETE | `src/generate_schemas.py`, 222 schema docs + `docs/schemas/README.md` |
| 8 | `task-05-verify` | Data Engineer + Tester | Lead | `task-03-transform`, `task-02b-parse-plan` | ✅ COMPLETE | `src/verify.py`, `docs/verification_report.md` (277 PASS / 22 EXEMPT / 0 non-exempt FAIL) |
| 9 | `task-06-pipeline` | Data Engineer | Tester, Scribe, Lead | tasks 01-05 | 🔶 HUMAN BLOCKED | `run_pipeline.py` (46 tests pass), root `README.md` — blocked on `www.cbo.gov` DNS in sandbox |

## Review Routing Notes

- **Lead** reviews architecture-sensitive work: inspection findings, parse plan, transform overrides, and tolerance exceptions.
- **Tester** writes test plans early and validates every build slice against task acceptance criteria.
- **Scribe** joins after each substantial slice to keep decisions and docs current, and performs the final schema/README prose pass.

## Entry Criteria for Build

- Task owners and reviewers are aligned with `.squad/routing.md`.
- Each task file includes explicit inputs, outputs, dependencies, and unambiguous acceptance criteria.
- Build starts with `task-01-download` and should not skip the parse-plan handoff.

## Exit Criteria for Returning to Validate

- Tasks 01-06 and `task-02b-parse-plan` are implemented.
- `.squad/decisions.md` records material parser and verification decisions.
- `.squad/validation_report.md` can be produced from passing checks.
