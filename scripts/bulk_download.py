"""
Bulk download all CBO baseline xlsx files via Wayback Machine.
For each URL, tries timestamps starting ~3 months after the file's release date.
"""
import hashlib
import json
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
SESSION = requests.Session()

# All 244 xlsx URLs from the CBO index page (archived 2026-03-11)
ALL_URLS = [
    "https://www.cbo.gov/system/files/2026-02/59126-2026-02-aatf.xlsx",
    "https://www.cbo.gov/system/files/2025-01/59126-2025-01-aatf.xlsx",
    "https://www.cbo.gov/system/files/2024-06/59126-2024-06-aatf.xlsx",
    "https://www.cbo.gov/system/files/2024-02/59126-2024-02-aatf.xlsx",
    "https://www.cbo.gov/system/files/2023-05/59126-2023-05-aatf_0.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51293-2026-02-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51293-2025-01-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51293-2024-06-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51293-2024-02-childnutrition_0.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51293-2023-05-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51293-2022-05-childnutrition_0.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51293-2021-07-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51293-2021-02-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51293-2020-03-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51293-2020-01-childnutrition.xlsx",
    "https://www.cbo.gov/system/files/2019-07/51293-2019-05-Child-Nutrition.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51295-2026-02-csec.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51295-2025-01-csec.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51295-2024-06-csec.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51295-2024-02-csec.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51295-2023-05-csec.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51295-2022-05-csec_0.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51295-2021-07-childsupportenforcement.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51295-2021-02-childsupportenforcement.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51295-2020-03-childsupportenforcement.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51295-2020-01-childsupportenforcement.xlsx",
    "https://www.cbo.gov/system/files/2019-07/51295-2019-05-Child-Support-Enforcement.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51296-2026-02-chip.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51296-2024-06-chip.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51296-2023-05-chip.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51296-2022-05-chip.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51296-2021-07-chip.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51296-2020-03-chip.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51296-2019-05-CHIP.xlsx",
    "https://www.cbo.gov/system/files/2026-02/61170-2026-02-customs-fees.xlsx",
    "https://www.cbo.gov/system/files/2025-01/61170-2025-01-customs-fees.xlsx",
    "https://www.cbo.gov/system/files/2026-02/54946-2026-02-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2025-01/54946-2025-01-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2024-02/54946-2024-02-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2023-05/54946-2023-05-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2022-05/54946-2022-05-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2021-07/54946-2021-07-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2021-02/54946-2021-02-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2020-03/54946-2020-03-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2020-01/54946-2020-01-dodmedicare.xlsx",
    "https://www.cbo.gov/system/files/2019-11/54946-2019-05-DoDMedicare.xlsx",
    "https://www.cbo.gov/system/files/2025-01/60394-2025-01-fdic.xlsx",
    "https://www.cbo.gov/system/files/2024-06/60394-2024-06-fdic.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51297-2024-06-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51297-2023-05-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51297-2022-05-mortgages_0.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51297-2021-07-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51297-2021-02-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51297-2020-03-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51297-2020-01-mortgages.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51297-2019-05-Mortgages.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51298-2026-02-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51298-2024-06-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2023-09/51298-2023-09-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51298-2023-05-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2022-06/51298-2022-06-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2021-08/51298-2021-07-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2020-10/51298-2020-09-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51298-2020-03-healthinsurance.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51298-2019-05-Health-Insurance.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51299-2026-02-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51299-2025-01-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51299-2024-06-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51299-2024-02-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51299-2023-05-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51299-2022-05-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51299-2021-07-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51299-2021-02-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51299-2020-03-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51299-2020-01-fostercare.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51299-2019-05-foster-care%20.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51300-2026-02-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51300-2025-01-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51300-2024-06-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51300-2024-02-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51300-2023-05-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51300-2022-05-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51300-2021-07-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51300-2021-02-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51300-2020-03-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51300-2020-01-highwaytrustfund.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51300-2019-05-Highway-Trust-Fund.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51301-2026-02-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51301-2024-06-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51301-2023-05-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51301-2022-05-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51301-2021-07-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51301-2020-03-medicaid.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51301-2019-05-Medicaid.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51302-2026-02-medicare.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51302-2024-06-medicare.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51302-2023-05-medicare.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51302-2022-05-medicare.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51302-2021-07-medicare.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51302-2020-03-medicare.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51302-2019-05-Medicare.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51303-2024-06-militaryretirement.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51303-2023-05-militaryretirement.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51303-2022-05-militaryretirement_0.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51303-2021-02-militaryretirement.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51303-2020-03-militaryretirement.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51303-2020-01-militaryretirement.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51303-2019-05-Military-Retirement.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51304-2026-02-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51304-2025-01-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51304-2024-06-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51304-2023-05-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51304-2022-05-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51304-2021-07-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51304-2021-02-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51304-2020-03-pellgrant_0.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51304-2020-01-pellgrant.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51304-2019-05-Pell-Grant.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51305-2024-06-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51305-2023-05-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51305-2022-05-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51305-2021-07-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51305-2021-02-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51305-2020-03-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51305-2020-01-pbgc.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51305-2019-05-PBGC.xlsx",
    "https://www.cbo.gov/system/files/2024-02/53726-2024-02-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2023-05/53726-2023-05-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2022-05/53726-2022-05-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2021-07/53726-2021-07-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2021-02/53726-2021-02-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2020-03/53726-2020-03-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2020-01/53726-2020-01-post911gibill.xlsx",
    "https://www.cbo.gov/system/files/2019-12/53726-2019-05-Post911-GI-Bill.xlsx",
    "https://www.cbo.gov/system/files/2026-02/60523-2026-02-premium-tax-credit.xlsx",
    "https://www.cbo.gov/system/files/2024-07/60523-2024-07-premium-tax-credit.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51306-2026-02-railroadretirement.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51307-2026-02-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51307-2025-01-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51307-2024-06-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51307-2024-02-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51307-2023-05-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51307-2022-05-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51307-2021-07-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51307-2021-02-ssdi..xlsx",
    "https://www.cbo.gov/system/files/2020-03/51307-2020-03-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51307-2020-01-ssdi.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51307-2019-05-SSDI.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51308-2026-02-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51308-2025-01-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51308-2024-06-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51308-2024-02-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51308-2023-05-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51308-2022-05-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51308-2021-07-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51308-2021-02-socialsecurity..xlsx",
    "https://www.cbo.gov/system/files/2020-03/51308-2020-03-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51308-2020-01-socialsecurity.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51308-2019-05-Social-Security.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51309-2026-02-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51309-2025-01-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51309-2024-06-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51309-2024-02-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51309-2023-05-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51309-2022-05-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51309-2021-07-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51309-2021-02-sstrustfund.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51309-2020-03-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51309-2020-01-trustfund.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51309-2019-05-Trust-Funds.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51310-2024-06-studentloan.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51310-2023-05-studentloan.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51310-2022-05-studentloan.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51310-2021-07-studentloan.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51310-2020-03-studentloan.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51310-2019-05-Student-Loan.xlsx",
    "https://www.cbo.gov/system/files/2026-01/51312-2026-02-snap.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51312-2025-01-snap.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51312-2024-06-snap.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51312-2024-02-snap.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51312-2023-05-snap.xlsx",
    "https://www.cbo.gov/system/files/2023-02/51312-2023-02-snap.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51312-2022-05-snap.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51312-2021-07-snap.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51312-2021-02-snap.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51312-2020-03-snap.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51312-2020-01-snap.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51312-2019-05-SNAP.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51313-2026-02-ssi.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51313-2025-01-ssi.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51313-2024-06-ssi.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51313-2024-02-ssi.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51313-2023-05-ssi.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51313-2022-05-ssi.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51313-2021-07-ssi.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51313-2021-02-ssi.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51313-2020-03-ssi.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51313-2020-01-ssi_1.xlsx",
    "https://www.cbo.gov/system/files/2019-12/51313-2019-05-SSI.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51314-2026-02-tanf.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51314-2025-01-tanf.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51314-2024-06-tanf.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51314-2024-02-tanf.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51314-2023-05-tanf.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51314-2022-05-tanf.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51314-2021-07-tanf.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51314-2021-02-tanf.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51314-2020-03-tanf.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51314-2020-01-tanf.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51314-2019-05-TANF.xlsx",
    "https://www.cbo.gov/system/files/2026-02/60044-2026-02-tef.xlsx",
    "https://www.cbo.gov/system/files/2025-01/60044-2025-01-tef.xlsx",
    "https://www.cbo.gov/system/files/2024-06/60044-2024-06-tef.xlsx",
    "https://www.cbo.gov/system/files/2024-03/60044-2024-02-Toxic-Exposures-Fund.xlsx",
    "https://www.cbo.gov/system/files/2026-02/51316-2026-02-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51316-2025-01-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51316-2024-06-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51316-2024-02-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51316-2023-05-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51316-2022-05-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51316-2021-07-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51316-2021-02-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51316-2020-03-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51316-2020-01-unemployment.xlsx",
    "https://www.cbo.gov/system/files/2019-11/51316-2019-05-Unemployment.xlsx",
    "https://www.cbo.gov/system/files/2026-01/51317-2026-02-usda.xlsx",
    "https://www.cbo.gov/system/files/2025-01/51317-2025-01-usda.xlsx",
    "https://www.cbo.gov/system/files/2024-06/51317-2024-06-usda.xlsx",
    "https://www.cbo.gov/system/files/2024-02/51317-2024-02-usda.xlsx",
    "https://www.cbo.gov/system/files/2023-05/51317-2023-05-usda.xlsx",
    "https://www.cbo.gov/system/files/2023-02/51317-2023-02-usda.xlsx",
    "https://www.cbo.gov/system/files/2022-05/51317-2022-05-usda.xlsx",
    "https://www.cbo.gov/system/files/2021-07/51317-2021-07-usda.xlsx",
    "https://www.cbo.gov/system/files/2021-02/51317-2021-02-usda.xlsx",
    "https://www.cbo.gov/system/files/2020-03/51317-2020-03-usda.xlsx",
    "https://www.cbo.gov/system/files/2020-01/51317-2020-01-usda.xlsx",
    "https://www.cbo.gov/system/files/2025-01/53725-2025-01-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2024-02/53725-2024-02-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2023-05/53725-2023-05-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2022-05/53725-2022-05-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2021-02/53725-2021-02-veteransbenefit..xlsx",
    "https://www.cbo.gov/system/files/2020-03/53725-2020-03-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2020-01/53725-2020-01-veteransbenefit.xlsx",
    "https://www.cbo.gov/system/files/2019-11/53725-2019-05-Veterans.xlsx",
]


def url_to_filename(url: str) -> str:
    """Derive local filename from CBO URL, URL-decoding percent-encoded chars."""
    path = urllib.parse.urlparse(url).path
    raw = Path(path).name
    return urllib.parse.unquote(raw)


def try_download(url: str) -> bytes | None:
    """Try the known-good index snapshot first (if_ redirects to closest),
    then a few static fallback timestamps."""
    TIMESTAMPS = [
        "20260311132528",  # archived CBO index page — if_ finds nearest copy
        "20250601000000",
        "20241201000000",
        "20240101000000",
        "20230601000000",
        "20220601000000",
        "20210601000000",
        "20200601000000",
    ]
    for ts in TIMESTAMPS:
        wb_url = f"https://web.archive.org/web/{ts}if_/{url}"
        try:
            r = SESSION.get(wb_url, headers=HEADERS, timeout=20, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 5000 and r.content[:2] == b"PK":
                return r.content
            # If we got a clear 404, no point trying earlier timestamps
            if r.status_code == 404:
                break
        except requests.RequestException:
            pass
    return None


def main() -> None:
    discovered_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # Load existing manifest
    manifest_path = OUTPUT_DIR / "manifest.json"
    existing: list[dict] = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    existing_fnames = {e["filename"] for e in existing}

    new_entries: list[dict] = []
    failed: list[str] = []

    total = len(ALL_URLS)
    for i, url in enumerate(ALL_URLS, 1):
        filename = url_to_filename(url)
        dest = OUTPUT_DIR / filename

        if dest.exists():
            print(f"[{i}/{total}] SKIP (exists): {filename}")
            if filename not in existing_fnames:
                content = dest.read_bytes()
                new_entries.append({
                    "filename": filename, "source_url": url,
                    "discovered_at": discovered_at, "downloaded_at": None,
                    "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
                })
            continue

        print(f"[{i}/{total}] Downloading: {filename} ...", end=" ", flush=True)
        content = try_download(url)
        if content:
            dest.write_bytes(content)
            downloaded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            new_entries.append({
                "filename": filename, "source_url": url,
                "discovered_at": discovered_at, "downloaded_at": downloaded_at,
                "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content),
            })
            print(f"OK ({len(content):,} bytes)")
        else:
            failed.append(url)
            print("FAILED")

        time.sleep(0.4)

    # Update manifest
    combined = existing + [e for e in new_entries if e["filename"] not in existing_fnames]
    manifest_path.write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")

    on_disk = len(list(OUTPUT_DIR.glob("*.xlsx")))
    print(f"\n=== Done ===")
    print(f"Files on disk: {on_disk}")
    print(f"Manifest entries: {len(combined)}")
    print(f"Failed ({len(failed)}):")
    for f in failed:
        print(f"  {f}")


if __name__ == "__main__":
    main()
