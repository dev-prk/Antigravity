# Traffic Violations Insight System — Automated EDA & Data Quality Report

## 1. Data Cleaning & Audit Summary
- **Source File**: `traffic_violations_sample_raw.csv`
- **Raw Records Processed**: `12,000`
- **Cleaned Records**: `12,000` (`10,560` unique `SeqID` traffic stops)
- **Multi-Charge Rows Flagged**: `2,777`
- **Coordinates Recovered from `Geolocation`**: `300` (`99.08%` valid US coordinates)
- **Out-of-Bounds Vehicle Years Sanitized (`<1960` or `>2025`)**: `200`

## 2. Top Violation Categories
- **License / Registration / Insurance**: `2,332` (`19.4%`)
- **Traffic Signal / Stop Sign**: `2,306` (`19.2%`)
- **Distracted Driving**: `1,269` (`10.6%`)
- **DUI / Alcohol**: `1,259` (`10.5%`)
- **Seatbelt / Restraint**: `1,250` (`10.4%`)

## 3. High-Risk Corridors & Hotspots
- **VEIRS MILL RD @ RANDOLPH RD**: `1,247` stops
- **WISCONSIN AVE @ EAST WEST HWY**: `1,244` stops
- **GEORGIA AVE @ COLESVILLE RD**: `1,232` stops
- **NEW HAMPSHIRE AVE @ LOCKWOOD DR**: `1,226` stops
- **FREDERICK RD @ SHADY GROVE RD**: `1,223` stops

## 4. Safety & Accident Risk Insights
- **Overall Accident-Linked Violations**: `5.74%`
- **Accident Rate When Alcohol Involved**: `12.65%`
- **Top Vehicle Makes Stopped**: TOYOTA (2,065), FORD (2,023), HONDA (1,926), SUBARU (1,019), HYUNDAI (1,008)
