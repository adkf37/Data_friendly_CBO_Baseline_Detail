# Data Sources - Data_friendly_CBO_Baseline_Detail

## Primary Source

| Field | Value |
|---|---|
| Name | CBO Baseline Projections for Selected Programs |
| URL | https://www.cbo.gov/data/baseline-projections-selected-programs |
| Owner | Congressional Budget Office (CBO) |
| Format | Excel (.xlsx) and PDF per program |
| Frequency | Updated roughly annually (after each baseline release) |
| License | Public domain (U.S. government work) |
| Availability | ✅ Publicly accessible, no authentication required |

## Discovery Approach

The CBO page at the URL above lists download links for each program. The pipeline will:
1. Fetch the HTML of the index page.
2. Parse all `.xlsx` download links (ignoring `.pdf` links).
3. Download each file to `data/raw/<program_slug>.xlsx`.

Because CBO does not publish a machine-readable manifest (API or JSON feed), link discovery relies on HTML scraping of the index page.

## Known Programs (as of 2026-05)

The page typically includes Excel files for the following program categories (exact file names vary by release year):

| Category | Programs (examples) |
|---|---|
| Health | Medicaid, Medicare, Health Insurance Subsidies, CHIP |
| Income Security | SNAP, SSI, TANF, Unemployment Compensation |
| Social Security | OASDI (Old-Age and Survivors Insurance), DI (Disability Insurance) |
| Veterans | VA Disability Compensation, VA Pension |
| Federal Employees | Federal Civilian Retirement, Military Retirement |
| Other | Student Loans, Fannie Mae/Freddie Mac, Deposit Insurance |

The exact list and file count will be determined at runtime by the discovery scrape.

## Constraints and Notes

- CBO may reorganize the page layout between baseline updates; the scraper should be resilient to minor HTML changes.
- Some Excel files contain multiple sheets that map to separate logical datasets (e.g., enrollment vs. spending). Each sheet is a candidate for its own output CSV.
- Units vary by program (billions of dollars, millions of beneficiaries, etc.) and must be captured in the schema.
- Fiscal year columns in source files typically span 10 years of projections plus several years of historical actuals.
