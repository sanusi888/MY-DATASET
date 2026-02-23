# Dynamics NAV Financial Dataset Generator

Professional synthetic dataset generator for enterprise ERP finance simulation, including IFRS mapping, intercompany transactions, treasury signals, cashflow behavior, and audit trail generation.

## Overview

This project generates two portfolio-ready CSV outputs:

1. **Financial Ledger Dataset** (`Dynamics_NAV_Financials_150K_Enterprise.csv` by default, otherwise `Dynamics_NAV_Financials_<rows>_Enterprise.csv`)
2. **Audit Journal Dataset** (`Dynamics_NAV_Audit_Journals_150K_Enterprise.csv` by default, otherwise `Dynamics_NAV_Audit_Journals_<rows>_Enterprise.csv`)

The generator is intended for:
- Analytics and BI portfolio projects
- IFRS reporting demonstrations
- Audit simulation and internal control walkthroughs
- Treasury and cashflow training scenarios
- ERP data engineering practice

## Features

- 150,000-row default generation volume
- Deterministic seed for reproducibility (`np.random.seed(42)`)
- Enterprise dimensions (department, cost center, subsidiary, segment)
- IFRS-standard tagging per GL account
- Multi-currency transactions with FX conversion into group currency
- Intercompany scenario modeling (`Intercompany_Flag`, `Intercompany_To`)
- A/R and A/P style due date and aging derivations
- Audit event chain per document (`Created`, `Approved/Posted`, `Adjusted/Reversed`)
- Built-in validation guardrails for deployment safety

## Output Files

### 1) Financial Dataset
**Filename:** `Dynamics_NAV_Financials_150K_Enterprise.csv` (default)

**Non-default pattern:** `Dynamics_NAV_Financials_<rows>_Enterprise.csv`

Representative columns include:
- Transaction identity: `Document_No`, `Posting_Date`, `Transaction_Type`
- Accounting: `Account_No`, `Account_Name`, `Category`, `IFRS_Standard`
- Org dimensions: `Subsidiary`, `Group_Company`, `Department`, `Cost_Center`, `Reporting_Segment`
- Monetary: `Amount`, `Currency`, `FX_Rate`, `Amount_Group_Currency`, `Group_Currency`
- Controls/workflow: `Posted_By`, `Approved`, `Status`, `Memo`, `Tax_Code`
- Cashflow/treasury: `Cashflow_Type`, `Expected_Cashflow_Date`, `Bank_Account`
- Receivables/payables timing: `Payment_Term_Days`, `Due_Date`, `Days_Overdue`, `Aging_Bucket`
- Intercompany: `Intercompany_Flag`, `Intercompany_To`, `Counterparty_ID`

### 2) Audit Journals
**Filename:** `Dynamics_NAV_Audit_Journals_150K_Enterprise.csv` (default)

**Non-default pattern:** `Dynamics_NAV_Audit_Journals_<rows>_Enterprise.csv`

Representative columns include:
- `Audit_ID`, `Document_No`, `Action_Type`
- `Performed_By`, `Performed_On`
- `Previous_Amount`, `New_Amount`
- `Previous_Status`, `New_Status`
- `Memo`, `Cost_Center`, `Subsidiary`, `Intercompany_Flag`

## Quick Start

### Prerequisites
- Python 3.9+
- `pandas`
- `numpy`

### Install dependencies
```bash
pip install pandas numpy
```

### Run
```bash
python dynamics_nav_financial_dataset_generator.py
```

### Optional runtime controls
```bash
python dynamics_nav_financial_dataset_generator.py --rows 10000 --seed 42
```

## Validation Checks

During execution, the script validates:
- Non-empty financial and audit outputs
- Unique `Document_No` per financial record
- FX consistency (`Amount * FX_Rate == Amount_Group_Currency`, rounded)
- `Days_Overdue` consistency against `Due_Date` and fixed `AS_OF_DATE`
- Presence of `Intercompany_To` for intercompany rows
- Intercompany `Counterparty_ID` alignment with `Intercompany_To`
- Audit-document referential integrity against the financial dataset

If validation succeeds, the script prints:

```text
Validation checks passed.
```

## Deployment Notes

- Default output volume is **150,000** rows for the financial dataset.
- Keep this default for full-scale portfolio/demonstration output.
- Optional lower volumes (`--rows`) should be used only for faster smoke tests.


## Scalable Analytics Stack (ETL + SQL + DAX)

This repository includes production-style assets to operationalize analytics beyond raw CSV files:

- `etl_nav_analytics_pipeline.py`
  - Builds a star-schema-ready model (`DimDate`, `DimAccount`, `DimDepartment`, `DimSubsidiary`, `FactFinancial`, `FactAudit`) plus `KpiMonthly` aggregate output.
  - Supports `--output-format parquet|csv` for scalable storage choices.

- `sql/nav_analytics_schema.sql`
  - SQL Server warehouse DDL for dimensions/facts, indexes, and a ratio base view `vw_Financial_Ratio_Base`.

- `dax/nav_ratio_measures.dax`
  - Ready-to-use ratio measures (Gross Margin %, Operating Margin %, OPEX Ratio %, COGS Ratio %, Approval/Posted rates, intercompany ratios).

### ETL run example

```bash
python etl_nav_analytics_pipeline.py \
  --financial-csv Dynamics_NAV_Financials_150K_Enterprise.csv \
  --audit-csv Dynamics_NAV_Audit_Journals_150K_Enterprise.csv \
  --output-dir analytics_output \
  --output-format parquet
```

### Scalable implementation steps

1. Generate validated source CSVs from the dataset generator.
2. Run `etl_nav_analytics_pipeline.py` to materialize star-schema analytics tables.
3. Load model tables into SQL Server using `sql/nav_analytics_schema.sql`.
4. Connect Power BI to SQL model/facts and paste measures from `dax/nav_ratio_measures.dax`.
5. Schedule ETL (Task Scheduler / CI runner) and monitor row-count + integrity checks each run.

## Copyright

© 2026 Sanusi Opeyemi Sanusi. All rights reserved.

Unless explicitly stated otherwise in a separate license file, no part of this repository may be reproduced, distributed, or used for commercial purposes without prior written permission from the copyright holder.

## Trademark Notice

- **Microsoft**, **Microsoft Dynamics**, and **Dynamics NAV** are trademarks of Microsoft Corporation.
- This project is an independent educational and portfolio dataset generator and is **not** affiliated with, endorsed by, or sponsored by Microsoft Corporation.
- Any other product names, company names, or marks appearing in generated sample data are used for simulation and identification purposes only.

## Disclaimer

This repository generates **synthetic/sample** financial data for training, analytics, and demonstration. It is not intended to represent real company ledgers, legal advice, accounting advice, or regulatory filings.
