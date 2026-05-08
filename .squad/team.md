# Squad Team

> Data_friendly_CBO_Baseline_Detail

## Coordinator

| Name | Role | Notes |
|------|------|-------|
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. Maestro is the outer work queue; Squad coordinates repo-local execution. |

## Members

| Name | Role | Charter | Status |
|------|------|---------|--------|
| Lead | Squad Lead | [charter](.squad/agents/lead/charter.md) | Active |
| Data Engineer | Pipeline Developer | [charter](.squad/agents/data-engineer/charter.md) | Active |
| Tester | QA & Validation | [charter](.squad/agents/tester/charter.md) | Active |
| Scribe | Documentation Specialist | [charter](.squad/agents/scribe/charter.md) | Active |

## Retired Members

| Name | Role | Reason |
|------|------|--------|
| Ralph | Persistent Memory Agent | Retired — Maestro drives the work queue; Ralph has no role in a Maestro-orchestrated repo. Artifacts in `.squad/agents/_alumni/ralph/`. |

## Project Context

- **Project:** Data_friendly_CBO_Baseline_Detail
- **Type:** data_pipeline
- **Created:** 2026-05-08
- **Goal:** Reproducible Python pipeline — download ~30 CBO Excel files, transform to tidy CSVs, generate schemas, verify output fidelity.
