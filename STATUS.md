# STATUS - Data_friendly_CBO_Baseline_Detail

| Field | Value |
|---|---|
| Phase | build-task-03-transform-remaining-programs |
| Next Action | Validate |
| Last Updated | 2026-05-11 |
| Squad Template | data_pipeline |
| Priority | low |
| Blocking | None |
| GitHub Repo | https://github.com/adkf37/Data_friendly_CBO_Baseline_Detail |

## Current Objective

Complete **Build** for **Task ID: `task-03-transform`** (remaining-programs slice) by adding a `remaining-programs` slice to `src/transform.py` that covers all parse-plan sheets not matched by health or income-security keywords, exposing it through the CLI as `--slice remaining-programs`, and verifying with a new regression test.

## Recent Activity

- 2026-05-11: Build advanced for **Task ID: `task-03-transform`** (remaining-programs slice) — added `remaining-programs` to `SLICE_CHOICES` and extended `_in_slice` in `src/transform.py` so the new slice selects all included parse-plan datasets that are not matched by health or income-security keywords. Added regression test `test_run_transform_remaining_programs_slice_excludes_health_and_income_security`. Full unittest suite passes 12 tests. Routed to Validate.
- 2026-05-11: Closeout completed for **Task ID: `task-03-transform`** (income security slice) — independently rechecked the task acceptance criteria, latest validation report, full unittest suite, repo-root CLI help, a real `python src/transform.py --slice income-security --output-dir /tmp/cbo_closeout_income` run, and an output-integrity audit. Confirmed all 118 included income-security parse-plan entries were accounted for via CSV output or explicit parse-error logging, 72 datasets were written with the required headers, duplicate keys remained at 0, and `implausible_year_rows=0`. Returned the repo to **Build** for the remaining-programs slice of `task-03-transform`.
- 2026-05-11: Validate passed for **Task ID: `task-03-transform`** (income security slice) — dependency install, full unittest suite, CLI smoke check, real income-security transform run, and output-integrity audit completed. All 118 included income-security parse-plan entries were accounted for via CSV output or explicit parse-error logging, 72 datasets were written with the required headers, duplicate keys remained at 0, and `implausible_year_rows=0`. Routed to Closeout with 37 explicit parse errors preserved as follow-up risk in `parse_errors.log`.
- 2026-05-11: Build advanced for **Task ID: `task-03-transform`** (income security slice) — routed the sprint's next unfinished item to the Data Engineer/Tester path in `.squad/routing.md`, added explicit `--slice income-security` handling in `src/transform.py`, and added regression test `test_run_transform_income_security_slice_excludes_health_datasets`. `python -m unittest discover -s tests -v` now passes 10 tests, and a real `python src/transform.py --slice income-security --output-dir /tmp/cbo_transform_income` smoke run wrote 72 income-security datasets with 37 explicit parse errors surfaced in `parse_errors.log`. Routed to Validate.
- 2026-05-11: Tasks 01, 02, and 02b marked complete. Generated `config/workbook_parse_plan.yaml` (230 workbooks, 335 sheets, 299 included). Advanced to Build for `task-03-transform`.

## Remaining Follow-up

- **Next task:** Validate the remaining-programs slice of **`task-03-transform`** (run the full unittest suite, CLI smoke check, and real `--slice remaining-programs` transform run).
- Known parser-improvement follow-up: 37 explicit income-security parse errors and 14 health-slice parse errors remain in `data/processed/parse_errors.log`; these should guide later parser-improvement work for remaining programs.
- Schema generation, verification, and pipeline handoff remain downstream and cannot close out until transform coverage is finished.

## Artifacts

| Artifact | Location | Status |
|---|---|---|
| STATUS.md | `./STATUS.md` | updated |
| FEEDBACK.md | `./FEEDBACK.md` | created |
| Backlog README | `./backlog/README.md` | created |
| Task: Transform | `./backlog/tasks/task-03-transform.md` | active |
| Parse plan | `./config/workbook_parse_plan.yaml` | created |
| Validation report | `./.squad/validation_report.md` | updated for income-security Validate evidence |
| Review report | `./.squad/review_report.md` | updated for income-security Closeout decision |
| Squad decisions | `./.squad/decisions.md` | updated with remaining-programs Build decision |
| Root README | `./README.md` | updated for income-security handoff |
| Transform implementation | `./src/transform.py` | updated (remaining-programs slice added) |
| Transform tests | `./tests/test_transform.py` | updated (remaining-programs regression test added) |
| Processed outputs | `./data/processed/` | health slice available; income-security closeout outputs generated in `/tmp/cbo_closeout_income` |

## Needs Human Input

- None at this time.
