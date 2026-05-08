# Squad Decisions

## Active Decisions

### 2026-05-08 — Squad Init complete (squad-init phase)

**Decision:** Team composition set to Lead, Data Engineer, Tester, Scribe. Ralph retired.
**Rationale:** Maestro owns the outer work queue; Ralph's persistent-memory role is redundant in a Maestro-orchestrated repo. Four-agent team covers the full lifecycle of a data-pipeline project: architecture (Lead), ETL implementation (Data Engineer), quality assurance (Tester), documentation (Scribe).
**Task:** squad-init phase

---

### 2026-05-08 — Output format: long/tidy CSV

**Decision:** All transformed outputs will use long (tidy) format with columns `program`, `category`, `fiscal_year`, `value`, `unit`.
**Rationale:** Long format is most flexible for downstream analysis and visualization. Consistent column names make multi-program joins trivial.
**Task:** backlog/README.md, task-03-transform

---

### 2026-05-08 — Excel parsing library: openpyxl (not xlrd)

**Decision:** Use `openpyxl` for all Excel file reading.
**Rationale:** `openpyxl` supports `.xlsx` natively and does not execute macros. `xlrd` has dropped `.xlsx` support in recent versions. This aligns with the security requirement to not run embedded macros.
**Task:** task-02-inspect, task-03-transform

---

### 2026-05-08 — Scraping approach: HTML parsing (no official API)

**Decision:** Scrape the CBO index page HTML to discover `.xlsx` download links; skip `.pdf` links.
**Rationale:** CBO does not publish a machine-readable manifest. HTML parsing with `requests` + `BeautifulSoup` is the only practical discovery approach. Scraper should be resilient to minor HTML restructuring.
**Task:** task-01-download, backlog/data_sources.md

---

### 2026-05-08 — Squad review tightened build handoff

**Decision:** Add an explicit workbook parse-plan task between inspection and transform, and align task ownership/review with `.squad/routing.md`.
**Rationale:** Inspection findings alone are too loose for repeatable transform and verification work. A machine-readable parse plan closes the handoff gap, while corrected ownership makes sprint execution match the established squad roles.
**Task:** squad-review, task-02b-parse-plan, .squad/sprint.md

---

## Governance

- All meaningful changes require team consensus.
- Document architectural decisions here with the task ID that motivated the decision.
- Keep history focused on work, decisions focused on direction.
