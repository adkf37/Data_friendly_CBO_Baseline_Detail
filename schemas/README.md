# CBO Baseline Detail Schemas

Structural schemas are stable across vintages. Each logical dataset directory contains one `schema.json`; release-specific provenance and superscript notes live in the matching `.metadata.json` sidecar.

## Shared row schemas

- [`baseline_detail.schema.json`](baseline_detail.schema.json): standard baseline-detail rows.
- [`usda_baseline_detail.schema.json`](usda_baseline_detail.schema.json): standard rows plus USDA hierarchy fields.
- [`common_fields.schema.json`](common_fields.schema.json): shared field definitions and constraints.

## Dataset index

| Dataset | Program ID | Schema family | Releases | Dataset schema |
|---|---:|---|---:|---|
| Airport and Airway Trust Fund | `59126` | `baseline_detail` | 5 | [`schema.json`](../data/processed/airport_airway_trust_fund/schema.json) |
| Child Nutrition | `51293` | `baseline_detail` | 11 | [`schema.json`](../data/processed/child_nutrition/schema.json) |
| Child Support Enforcement | `51295` | `baseline_detail` | 11 | [`schema.json`](../data/processed/child_support_enforcement/schema.json) |
| CHIP | `51296` | `baseline_detail` | 7 | [`schema.json`](../data/processed/chip/schema.json) |
| Customs Fees | `61170` | `baseline_detail` | 2 | [`schema.json`](../data/processed/customs_fees/schema.json) |
| DoD Medicare | `54946` | `baseline_detail` | 10 | [`schema.json`](../data/processed/dod_medicare/schema.json) |
| FDIC | `60394` | `baseline_detail` | 2 | [`schema.json`](../data/processed/fdic/schema.json) |
| Foster Care | `51299` | `baseline_detail` | 11 | [`schema.json`](../data/processed/foster_care/schema.json) |
| Health Insurance | `51298` | `baseline_detail` | 9 | [`schema.json`](../data/processed/health_insurance/schema.json) |
| Highway Trust Fund | `51300` | `baseline_detail` | 12 | [`schema.json`](../data/processed/highway_trust_fund/schema.json) |
| Medicaid | `51301` | `baseline_detail` | 7 | [`schema.json`](../data/processed/medicaid/schema.json) |
| Medicare | `51302` | `baseline_detail` | 7 | [`schema.json`](../data/processed/medicare/schema.json) |
| Military Retirement | `51303` | `baseline_detail` | 7 | [`schema.json`](../data/processed/military_retirement/schema.json) |
| Mortgages | `51297` | `baseline_detail` | 8 | [`schema.json`](../data/processed/mortgages/schema.json) |
| PBGC | `51305` | `baseline_detail` | 8 | [`schema.json`](../data/processed/pbgc/schema.json) |
| Pell Grant | `51304` | `baseline_detail` | 10 | [`schema.json`](../data/processed/pell_grant/schema.json) |
| Post-9/11 GI Bill | `53726` | `baseline_detail` | 8 | [`schema.json`](../data/processed/post_911_gi_bill/schema.json) |
| Premium Tax Credit | `60523` | `baseline_detail` | 2 | [`schema.json`](../data/processed/premium_tax_credit/schema.json) |
| Railroad Retirement | `51306` | `baseline_detail` | 1 | [`schema.json`](../data/processed/railroad_retirement/schema.json) |
| SNAP | `51312` | `baseline_detail` | 12 | [`schema.json`](../data/processed/snap/schema.json) |
| Social Security | `51308` | `baseline_detail` | 11 | [`schema.json`](../data/processed/social_security/schema.json) |
| Social Security Trust Funds | `51309` | `baseline_detail` | 11 | [`schema.json`](../data/processed/social_security_trust_funds/schema.json) |
| SSDI | `51307` | `baseline_detail` | 11 | [`schema.json`](../data/processed/ssdi/schema.json) |
| SSI | `51313` | `baseline_detail` | 11 | [`schema.json`](../data/processed/ssi/schema.json) |
| Student Loans | `51310` | `baseline_detail` | 7 | [`schema.json`](../data/processed/student_loans/schema.json) |
| TANF | `51314` | `baseline_detail` | 11 | [`schema.json`](../data/processed/tanf/schema.json) |
| Toxic Exposures Fund | `60044` | `baseline_detail` | 4 | [`schema.json`](../data/processed/toxic_exposures_fund/schema.json) |
| Unemployment Insurance | `51316` | `baseline_detail` | 11 | [`schema.json`](../data/processed/unemployment_insurance/schema.json) |
| USDA Farm Programs | `51317` | `usda_baseline_detail` | 11 | [`schema.json`](../data/processed/usda_farm_programs/schema.json) |
| Veterans Benefits | `53725` | `baseline_detail` | 8 | [`schema.json`](../data/processed/veterans_benefits/schema.json) |
