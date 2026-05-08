# Work Routing

How to decide who handles what in the CBO Baseline Detail data pipeline project.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Architecture & design decisions | Lead | Pipeline structure, output schema design, transform strategy |
| Scraping / download implementation | Data Engineer | `src/download.py`, CBO page scraping, manifest creation |
| Excel inspection / profiling | Data Engineer | `src/inspect.py`, sheet detection, header inference |
| Data transformation (ETL) | Data Engineer | `src/transform.py`, tidy CSV output, unit normalization |
| Schema generation | Data Engineer | `src/schema.py`, `docs/schemas/` files |
| Verification / reconciliation | Data Engineer + Tester | `src/verify.py`, totals matching |
| Pipeline entrypoint wiring | Data Engineer | `src/run_pipeline.py`, `Makefile` |
| Test writing (unit & integration) | Tester | `tests/`, fixtures, pytest parametrization |
| Validation report | Tester | `.squad/validation_report.md` |
| Documentation / schemas prose | Scribe | `docs/`, root `README.md`, schema descriptions |
| Decision logging | Lead (or Scribe if Lead forgets) | `.squad/decisions.md` |
| Status updates | Lead | `STATUS.md` |
| Session history | Scribe | Always background, never blocks |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Lead |
| `squad:lead` | Pick up issue and complete the work | Lead |
| `squad:data-engineer` | Pick up issue and complete the work | Data Engineer |
| `squad:tester` | Pick up issue and complete the work | Tester |
| `squad:scribe` | Pick up issue and complete the work | Scribe |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, the **Lead** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a module is being built, spawn the Tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. The Lead handles all `squad` (base label) triage.
