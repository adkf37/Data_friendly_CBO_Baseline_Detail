# Sprint Plan - Data_friendly_CBO_Baseline_Detail

Current lifecycle target: move from **Squad Review** to **Build** with one explicit, ordered execution plan.

## Ordered Build Queue

| Order | Task | Owner | Reviewers / Parallel Support | Depends On | Deliverables |
|---|---|---|---|---|---|
| 1 | `task-01-download` | Data Engineer | Tester | None | `src/download.py`, `data/raw/manifest.json`, downloaded workbooks |
| 2 | `task-02-inspect` | Data Engineer | Lead, Tester | `task-01-download` | `src/inspect.py`, `docs/inspection_report.md` |
| 3 | `task-02b-parse-plan` | Lead | Data Engineer, Tester | `task-02-inspect` | `config/workbook_parse_plan.yaml`, any related decision log entries |
| 4 | `task-03-transform` — health slice | Data Engineer | Lead, Tester | `task-02b-parse-plan` | first transform slice, parser notes, any parse errors |
| 5 | `task-03-transform` — income security slice | Data Engineer | Lead, Tester | health slice | second transform slice, parser notes |
| 6 | `task-03-transform` — remaining programs slice | Data Engineer | Lead, Tester | income security slice | final transform coverage, parser notes |
| 7 | `task-04-schema` | Data Engineer | Scribe | `task-03-transform` | `src/schema.py`/`src/generate_schemas.py`, `docs/schemas/` |
| 8 | `task-05-verify` | Data Engineer + Tester | Lead | `task-03-transform`, `task-02b-parse-plan` | `src/verify.py`, `docs/verification_report.md` |
| 9 | `task-06-pipeline` | Data Engineer | Tester, Scribe, Lead | tasks 01-05 | `run_pipeline.py`, root `README.md` |

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
