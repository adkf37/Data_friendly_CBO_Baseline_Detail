# Phases - Data_friendly_CBO_Baseline_Detail

This document maps the project work to Maestro lifecycle phases.

---

## Phase 1 · Planner ✅

**Goal:** Survey the repo, define the deliverable, identify data sources, and create the backlog.

**Outputs:**
- `backlog/README.md`
- `backlog/data_sources.md`
- `backlog/phases.md` (this file)
- `backlog/tasks/`
- `STATUS.md` updated
- `requirements.txt`

---

## Phase 2 · Squad Init

**Goal:** Bootstrap `.squad/` artifacts, assign roles, and align responsibilities to the backlog.

**Outputs:**
- `.squad/team.md` — roster (Lead, Data Engineer, Tester, Scribe)
- `.squad/routing.md` — task ownership rules
- `.squad/decisions.md` — decision log initialized
- `.squad/agents/*/charter.md` — one charter per agent
- `STATUS.md` updated to "ready for squad-review"

---

## Phase 3 · Squad Review

**Goal:** Tighten task definitions, surface risks, and produce an ordered sprint plan.

**Outputs:**
- `backlog/tasks/` refined with acceptance criteria and estimates
- `.squad/sprint.md` — ordered execution plan with owners and dependencies
- `STATUS.md` updated to "ready for build"

---

## Phase 4 · Build (iterative)

**Goal:** Implement the pipeline in slices, one task at a time.

**Slices (in order):**
1. **Download** — scrape CBO index page, download all Excel files to `data/raw/`.
2. **Inspect** — profile each Excel file (sheets, header rows, data ranges, units).
3. **Transform (health programs)** — parse and normalize health program Excel files.
4. **Transform (income security programs)** — parse and normalize income security files.
5. **Transform (remaining programs)** — parse and normalize all remaining files.
6. **Schema generation** — write schema files for every output CSV.
7. **Verification** — reconcile output totals against source Excel values.
8. **Pipeline runner** — wire all steps into a single reproducible entrypoint.

**Outputs per slice:**
- Working code in `src/`
- Output data in `data/processed/`
- Updated `.squad/decisions.md`
- Updated `STATUS.md`

---

## Phase 5 · Validate

**Goal:** Run automated checks, capture evidence, and decide whether to advance or return to Build.

**Checks:**
- All raw Excel files present in `data/raw/`
- All processed CSVs present and non-empty in `data/processed/`
- Schema files present for every CSV
- Verification report shows 0 reconciliation failures
- `requirements.txt` and pipeline runner tested in a clean environment

**Outputs:**
- `.squad/validation_report.md`
- `STATUS.md` updated with pass/fail/blocked outcome

---

## Phase 6 · Closeout

**Goal:** Refresh handoff artifacts and decide project status.

**Outputs:**
- `README.md` at repo root — end-to-end run instructions
- `.squad/review_report.md` — final review decision
- `STATUS.md` updated to `Complete` or `Human Blocked`
