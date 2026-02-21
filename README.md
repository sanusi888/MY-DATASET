 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..9677f53f840d4afd39d2b1502773fdcb286cd1af
--- /dev/null
+++ b/README.md
@@ -0,0 +1,108 @@
+# Dynamics NAV Financial Dataset Generator
+
+Professional synthetic dataset generator for enterprise ERP finance simulation, including IFRS mapping, intercompany transactions, treasury signals, cashflow behavior, and audit trail generation.
+
+## Overview
+
+This project generates two portfolio-ready CSV outputs:
+
+1. **Financial Ledger Dataset** (`Dynamics_NAV_Financials_150K_Enterprise.csv`)
+2. **Audit Journal Dataset** (`Dynamics_NAV_Audit_Journals_150K_Enterprise.csv`)
+
+The generator is intended for:
+- Analytics and BI portfolio projects
+- IFRS reporting demonstrations
+- Audit simulation and internal control walkthroughs
+- Treasury and cashflow training scenarios
+- ERP data engineering practice
+
+## Features
+
+- 150,000-row default generation volume
+- Deterministic seed for reproducibility (`np.random.seed(42)`)
+- Enterprise dimensions (department, cost center, subsidiary, segment)
+- IFRS-standard tagging per GL account
+- Multi-currency transactions with FX conversion into group currency
+- Intercompany scenario modeling (`Intercompany_Flag`, `Intercompany_To`)
+- A/R and A/P style due date and aging derivations
+- Audit event chain per document (`Created`, `Approved/Posted`, `Adjusted/Reversed`)
+- Built-in validation guardrails for deployment safety
+
+## Output Files
+
+### 1) Financial Dataset
+**Filename:** `Dynamics_NAV_Financials_150K_Enterprise.csv`
+
+Representative columns include:
+- Transaction identity: `Document_No`, `Posting_Date`, `Transaction_Type`
+- Accounting: `Account_No`, `Account_Name`, `Category`, `IFRS_Standard`
+- Org dimensions: `Subsidiary`, `Group_Company`, `Department`, `Cost_Center`, `Reporting_Segment`
+- Monetary: `Amount`, `Currency`, `FX_Rate`, `Amount_Group_Currency`, `Group_Currency`
+- Controls/workflow: `Posted_By`, `Approved`, `Status`, `Memo`, `Tax_Code`
+- Cashflow/treasury: `Cashflow_Type`, `Expected_Cashflow_Date`, `Bank_Account`
+- Receivables/payables timing: `Payment_Term_Days`, `Due_Date`, `Days_Overdue`, `Aging_Bucket`
+- Intercompany: `Intercompany_Flag`, `Intercompany_To`, `Counterparty_ID`
+
+### 2) Audit Journals
+**Filename:** `Dynamics_NAV_Audit_Journals_150K_Enterprise.csv`
+
+Representative columns include:
+- `Audit_ID`, `Document_No`, `Action_Type`
+- `Performed_By`, `Performed_On`
+- `Previous_Amount`, `New_Amount`
+- `Previous_Status`, `New_Status`
+- `Memo`, `Cost_Center`, `Subsidiary`, `Intercompany_Flag`
+
+## Quick Start
+
+### Prerequisites
+- Python 3.9+
+- `pandas`
+- `numpy`
+
+### Install dependencies
+```bash
+pip install pandas numpy
+```
+
+### Run
+```bash
+python dynamics_nav_financial_dataset_generator.py
+```
+
+## Validation Checks
+
+During execution, the script validates:
+- Non-empty financial output
+- Unique `Document_No` per financial record
+- FX consistency (`Amount * FX_Rate == Amount_Group_Currency`, rounded)
+- Presence of `Intercompany_To` for intercompany rows
+- Audit-document referential integrity against the financial dataset
+
+If validation succeeds, the script prints:
+
+```text
+Validation checks passed.
+```
+
+## Deployment Notes
+
+- Default output volume is **150,000** rows for the financial dataset.
+- Keep this default for full-scale portfolio/demonstration output.
+- Optional lower volumes (if later parameterized) should be used only for faster smoke tests.
+
+## Copyright
+
+© 2026 Sanusi Opeyemi Sanusi. All rights reserved.
+
+Unless explicitly stated otherwise in a separate license file, no part of this repository may be reproduced, distributed, or used for commercial purposes without prior written permission from the copyright holder.
+
+## Trademark Notice
+
+- **Microsoft**, **Microsoft Dynamics**, and **Dynamics NAV** are trademarks of Microsoft Corporation.
+- This project is an independent educational and portfolio dataset generator and is **not** affiliated with, endorsed by, or sponsored by Microsoft Corporation.
+- Any other product names, company names, or marks appearing in generated sample data are used for simulation and identification purposes only.
+
+## Disclaimer
+
+This repository generates **synthetic/sample** financial data for training, analytics, and demonstration. It is not intended to represent real company ledgers, legal advice, accounting advice, or regulatory filings.
 
EOF
)
