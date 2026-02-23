# Finance Go-Live UAT Checklist (1-Page)

**Project:** Dynamics NAV Enterprise Analytics Stack  
**Environment:** [DEV / UAT / PROD]  
**Test Cycle ID:** [UAT-YYYYMMDD-##]  
**Date:** [DD-MMM-YYYY]  
**Prepared by:** [NAME]  
**Reviewed by:** [NAME]  

---

## A) Pre-Run Setup Validation

| # | Check | Expected Result | Status (Pass/Fail) | Evidence / Notes |
|---|---|---|---|---|
| A1 | Python environment active | Correct virtual environment is active | [ ] Pass [ ] Fail | |
| A2 | Dependencies installed | `pandas` and `numpy` available | [ ] Pass [ ] Fail | |
| A3 | Source scripts available | Generator + ETL + SQL + DAX files present | [ ] Pass [ ] Fail | |

---

## B) Data Generation Validation

| # | Check | Expected Result | Status (Pass/Fail) | Evidence / Notes |
|---|---|---|---|---|
| B1 | Smoke run command | `python dynamics_nav_financial_dataset_generator.py --rows 10000 --seed 42` completes | [ ] Pass [ ] Fail | |
| B2 | Full run command | `python dynamics_nav_financial_dataset_generator.py` completes | [ ] Pass [ ] Fail | |
| B3 | Validation output | Console shows `Validation checks passed.` | [ ] Pass [ ] Fail | |
| B4 | Financial output file | Financial CSV created with expected naming | [ ] Pass [ ] Fail | |
| B5 | Audit output file | Audit CSV created with expected naming | [ ] Pass [ ] Fail | |

---

## C) ETL Validation

| # | Check | Expected Result | Status (Pass/Fail) | Evidence / Notes |
|---|---|---|---|---|
| C1 | ETL run command | `python etl_nav_analytics_pipeline.py --output-format parquet` completes | [ ] Pass [ ] Fail | |
| C2 | Model outputs | `DimDate`, `DimAccount`, `DimDepartment`, `DimSubsidiary`, `FactFinancial`, `FactAudit`, `KpiMonthly` produced | [ ] Pass [ ] Fail | |
| C3 | Data typing sanity | Numeric/date columns correctly parsed and persisted | [ ] Pass [ ] Fail | |

---

## D) SQL Warehouse Validation

| # | Check | Expected Result | Status (Pass/Fail) | Evidence / Notes |
|---|---|---|---|---|
| D1 | Schema deployment | `sql/nav_analytics_schema.sql` executes without errors | [ ] Pass [ ] Fail | |
| D2 | Table load | Dimension/fact tables loaded with non-zero records | [ ] Pass [ ] Fail | |
| D3 | Referential integrity | No FK violations in `FactFinancial`/`FactAudit` | [ ] Pass [ ] Fail | |
| D4 | Ratio view | `vw_Financial_Ratio_Base` returns expected grouped results | [ ] Pass [ ] Fail | |

---

## E) Power BI / DAX Validation

| # | Check | Expected Result | Status (Pass/Fail) | Evidence / Notes |
|---|---|---|---|---|
| E1 | Measures loaded | `dax/nav_ratio_measures.dax` measures added successfully | [ ] Pass [ ] Fail | |
| E2 | Profitability KPIs | Revenue, Gross Margin %, Operating Margin % display correctly | [ ] Pass [ ] Fail | |
| E3 | Control KPIs | Approval Rate % and Posted Rate % display correctly | [ ] Pass [ ] Fail | |
| E4 | Trend checks | Monthly/segment/subsidiary slicers recalculate correctly | [ ] Pass [ ] Fail | |

---

## F) Go-Live Decision

**Overall UAT Result:** [ ] PASS (Go-Live Approved)  [ ] FAIL (Remediation Required)

**Critical defects:** [None / List IDs]  
**Minor defects accepted:** [None / List IDs]  
**Rollback plan confirmed:** [ ] Yes  [ ] No

---

## Sign-Off Lines

**Finance Lead:** ____________________  **Date:** ___/___/_____  
**Data Engineering Lead:** ____________________  **Date:** ___/___/_____  
**BI/Reporting Lead:** ____________________  **Date:** ___/___/_____  
**Project Owner / Final Approver:** ____________________  **Date:** ___/___/_____

---

## Quick Evidence Commands (Optional)

```bash
python dynamics_nav_financial_dataset_generator.py --rows 10000 --seed 42
python dynamics_nav_financial_dataset_generator.py
python etl_nav_analytics_pipeline.py --output-format parquet
```
