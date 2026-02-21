"""
Dynamics NAV Financial Dataset Generator
(Global Enterprise + IFRS + Intercompany + Audit + Cashflow + Treasury)
Author: Sanusi Opeyemi Sanusi
Purpose: Generate simulated enterprise ERP dataset + audit journals
for portfolio, training, IFRS reporting, SOP compliance, treasury, cost accounting, and audit simulation.
Date: 2026-02-21
"""

import argparse
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# -----------------------------
# Settings
# -----------------------------
np.random.seed(42)

TOTAL_ROWS = 150000
START_DATE = datetime(2025, 1, 1)
DAYS = 365  # 1 year
GROUP_CURRENCY = "USD"
AS_OF_DATE = START_DATE + timedelta(days=DAYS)

# Departments and Cost Centers
DEPARTMENTS = [
    "Financial Management",
    "Sales and Marketing",
    "Purchasing",
    "Warehouse",
    "Manufacturing",
    "Jobs",
    "Resource Planning",
    "Service",
    "Human Resources",
    "Administrative",
    "Fleet Management",
]

DEPARTMENT_TO_COST_CENTER = {
    "Financial Management": "CC_Finance",
    "Sales and Marketing": "CC_Sales",
    "Purchasing": "CC_Purchasing",
    "Warehouse": "CC_Warehouse",
    "Manufacturing": "CC_Manufacturing",
    "Jobs": "CC_Jobs",
    "Resource Planning": "CC_ResourcePlanning",
    "Service": "CC_Service",
    "Human Resources": "CC_HR",
    "Administrative": "CC_Admin",
    "Fleet Management": "CC_Fleet",
}

# Subsidiaries
SBUS = [
    "SBU_1_Manufacturing",
    "SBU_2_SalesMarketing",
    "SBU_3_Service",
    "SBU_4_FleetLogistics",
    "SBU_5_JobsResource",
]
GROUP_COMPANY = "Group_Company"

# GL Accounts -> (account_no, category, account_name, ifrs_standard)
GL_ACCOUNTS = [
    ("4000", "Revenue", "Sales Revenue", "IFRS 15"),
    ("4010", "Revenue", "Service Revenue", "IFRS 15"),
    ("5000", "COGS", "Cost of Goods Sold", "IAS 2"),
    ("5100", "COGS", "Direct Materials", "IAS 2"),
    ("6000", "OPEX", "Operating Expenses", "IAS 1"),
    ("6100", "OPEX", "Marketing Expenses", "IAS 1"),
    ("6200", "OPEX", "Salaries & Wages", "IAS 19"),
    ("6300", "OPEX", "Fleet Expenses", "IAS 16"),
    ("6400", "OPEX", "Administrative Expenses", "IAS 1"),
    ("6500", "OPEX", "Training & HR Expenses", "IAS 19"),
]

# Transaction metadata
CURRENCIES = ["USD", "EUR", "GBP", "NGN"]
TRANSACTION_TYPES = [
    "Sales Invoice",
    "Purchase Invoice",
    "Payment",
    "Receipt",
    "Journal Entry",
    "Cash Advance",
    "Employee Reimbursement",
    "Retirement Settlement",
]
MEMOS = [
    "Monthly sale",
    "Purchase order",
    "Salary payment",
    "Fleet maintenance",
    "Cash advance issued",
    "Employee reimbursement",
    "Retirement settlement",
]
TAX_CODES = ["VAT_0", "VAT_5", "VAT_10"]
REPORTING_SEGMENTS = ["Industrial", "Commercial", "Corporate Services", "Logistics"]
BANK_ACCOUNTS = ["BANK_USD_MAIN", "BANK_EUR_MAIN", "BANK_GBP_MAIN", "BANK_NGN_OPS"]
VENDORS = [f"VENDOR_{i:03d}" for i in range(1, 151)]
CUSTOMERS = [f"CUSTOMER_{i:03d}" for i in range(1, 201)]

# Intercompany
INTERCOMPANY_PROB = 0.05
INTERCOMPANY_PAIRS = [
    ("SBU_1_Manufacturing", "SBU_2_SalesMarketing"),
    ("SBU_2_SalesMarketing", "SBU_3_Service"),
    ("SBU_3_Service", "SBU_4_FleetLogistics"),
    ("SBU_4_FleetLogistics", "SBU_5_JobsResource"),
    ("SBU_5_JobsResource", "SBU_1_Manufacturing"),
]


def _amount_for_category(category: str) -> int:
    if category == "Revenue":
        return np.random.randint(500, 5000)
    return -np.random.randint(100, 3000)


def _aging_bucket(days_overdue: int) -> str:
    if days_overdue <= 0:
        return "Current"
    if days_overdue <= 30:
        return "1-30"
    if days_overdue <= 60:
        return "31-60"
    if days_overdue <= 90:
        return "61-90"
    return "90+"


def generate_financial_dataset(total_rows: int = TOTAL_ROWS, output_path: str | None = None) -> pd.DataFrame:
    rows = []

    for i in range(total_rows):
        posting_date = START_DATE + timedelta(days=np.random.randint(0, DAYS))
        subsidiary = np.random.choice(SBUS)
        department = np.random.choice(DEPARTMENTS)
        account_no, category, account_name, ifrs_standard = GL_ACCOUNTS[np.random.randint(len(GL_ACCOUNTS))]

        amount = _amount_for_category(category)
        currency = np.random.choice(CURRENCIES)
        fx_rate = round(np.random.uniform(0.5, 1.5), 4)
        amount_group_currency = round(amount * fx_rate, 2)

        cost_adjustment_flag = np.random.choice([0, 1], p=[0.95, 0.05])
        original_doc_no = f"TX-{np.random.randint(1, total_rows + 1):06d}" if cost_adjustment_flag == 1 else ""

        cashflow_type = "Inflow" if category == "Revenue" else "Outflow"
        expected_cashflow_date = posting_date + timedelta(days=np.random.randint(0, 90))
        cost_center = DEPARTMENT_TO_COST_CENTER[department]

        payment_term_days = int(np.random.choice([0, 7, 14, 30, 45, 60], p=[0.05, 0.1, 0.15, 0.4, 0.2, 0.1]))
        due_date = posting_date + timedelta(days=payment_term_days)
        days_overdue = max((AS_OF_DATE - due_date).days, 0)
        aging_bucket = _aging_bucket(days_overdue)

        document_no = f"TX-{i + 1:06d}"
        counterparty = np.random.choice(CUSTOMERS if category == "Revenue" else VENDORS)

        rows.append(
            {
                "Posting_Date": posting_date.strftime("%Y-%m-%d"),
                "Subsidiary": subsidiary,
                "Group_Company": GROUP_COMPANY,
                "Department": department,
                "Cost_Center": cost_center,
                "Reporting_Segment": np.random.choice(REPORTING_SEGMENTS),
                "Account_No": account_no,
                "Account_Name": account_name,
                "Category": category,
                "IFRS_Standard": ifrs_standard,
                "Amount": amount,
                "Amount_Group_Currency": amount_group_currency,
                "Group_Currency": GROUP_CURRENCY,
                "Document_No": document_no,
                "Counterparty_ID": counterparty,
                "Currency": currency,
                "FX_Rate": fx_rate,
                "Transaction_Type": np.random.choice(TRANSACTION_TYPES),
                "Bank_Account": np.random.choice(BANK_ACCOUNTS),
                "Posted_By": f"User_{np.random.randint(1, 21)}",
                "Approved": np.random.choice([0, 1], p=[0.1, 0.9]),
                "Status": np.random.choice(["Draft", "Posted", "Reversed"]),
                "Memo": np.random.choice(MEMOS, p=[0.3, 0.2, 0.2, 0.1, 0.05, 0.1, 0.05]),
                "Tax_Code": np.random.choice(TAX_CODES),
                "Intercompany_Flag": 0,
                "Intercompany_To": "",
                "Cashflow_Type": cashflow_type,
                "Expected_Cashflow_Date": expected_cashflow_date.strftime("%Y-%m-%d"),
                "Payment_Term_Days": payment_term_days,
                "Due_Date": due_date.strftime("%Y-%m-%d"),
                "Days_Overdue": days_overdue,
                "Aging_Bucket": aging_bucket,
                "Cost_Adjustment_Flag": cost_adjustment_flag,
                "Original_Doc_No": original_doc_no,
            }
        )

    num_intercompany = int(total_rows * INTERCOMPANY_PROB)
    intercompany_idx = np.random.choice(range(total_rows), size=num_intercompany, replace=False)

    for idx in intercompany_idx:
        sbu_from, sbu_to = INTERCOMPANY_PAIRS[np.random.randint(len(INTERCOMPANY_PAIRS))]
        rows[idx]["Subsidiary"] = sbu_from
        rows[idx]["Intercompany_To"] = sbu_to
        rows[idx]["Department"] = np.random.choice(DEPARTMENTS)
        rows[idx]["Cost_Center"] = DEPARTMENT_TO_COST_CENTER[rows[idx]["Department"]]
        rows[idx]["Intercompany_Flag"] = 1
        rows[idx]["Counterparty_ID"] = sbu_to

        # Maintain directional amount semantics.
        if rows[idx]["Category"] != "Revenue":
            rows[idx]["Amount"] = -abs(rows[idx]["Amount"])

        rows[idx]["Amount_Group_Currency"] = round(rows[idx]["Amount"] * rows[idx]["FX_Rate"], 2)

    df_financial = pd.DataFrame(rows)
    if output_path is None:
        output_path = f"Dynamics_NAV_Financials_{total_rows}_Enterprise.csv"

    df_financial.to_csv(output_path, index=False)
    print("Financial dataset generated successfully!")
    return df_financial


def generate_audit_journals(df_financial: pd.DataFrame, output_path: str | None = None) -> pd.DataFrame:
    audit_rows = []
    audit_id = 1

    for _, tx in df_financial.iterrows():
        audit_rows.append(
            {
                "Audit_ID": audit_id,
                "Document_No": tx["Document_No"],
                "Action_Type": "Created",
                "Performed_By": tx["Posted_By"],
                "Performed_On": tx["Posting_Date"],
                "Previous_Amount": None,
                "New_Amount": tx["Amount"],
                "Previous_Status": None,
                "New_Status": tx["Status"],
                "Memo": tx["Memo"],
                "Cost_Center": tx["Cost_Center"],
                "Subsidiary": tx["Subsidiary"],
                "Intercompany_Flag": tx["Intercompany_Flag"],
            }
        )
        audit_id += 1

        if tx["Approved"] == 1:
            audit_rows.append(
                {
                    "Audit_ID": audit_id,
                    "Document_No": tx["Document_No"],
                    "Action_Type": "Approved/Posted",
                    "Performed_By": f"User_{np.random.randint(1, 21)}",
                    "Performed_On": (
                        pd.to_datetime(tx["Posting_Date"]) + timedelta(hours=np.random.randint(1, 48))
                    ).strftime("%Y-%m-%d"),
                    "Previous_Amount": None,
                    "New_Amount": tx["Amount"],
                    "Previous_Status": tx["Status"],
                    "New_Status": "Posted",
                    "Memo": "Approved by reviewer",
                    "Cost_Center": tx["Cost_Center"],
                    "Subsidiary": tx["Subsidiary"],
                    "Intercompany_Flag": tx["Intercompany_Flag"],
                }
            )
            audit_id += 1

        if tx["Cost_Adjustment_Flag"] == 1 or tx["Status"] == "Reversed":
            audit_rows.append(
                {
                    "Audit_ID": audit_id,
                    "Document_No": tx["Document_No"],
                    "Action_Type": "Adjusted/Reversed",
                    "Performed_By": f"User_{np.random.randint(1, 21)}",
                    "Performed_On": (
                        pd.to_datetime(tx["Posting_Date"]) + timedelta(days=np.random.randint(1, 5))
                    ).strftime("%Y-%m-%d"),
                    "Previous_Amount": tx["Amount"],
                    "New_Amount": tx["Amount"] + np.random.randint(-500, 500),
                    "Previous_Status": tx["Status"],
                    "New_Status": tx["Status"],
                    "Memo": "Adjustment entry",
                    "Cost_Center": tx["Cost_Center"],
                    "Subsidiary": tx["Subsidiary"],
                    "Intercompany_Flag": tx["Intercompany_Flag"],
                }
            )
            audit_id += 1

    df_audit = pd.DataFrame(audit_rows)
    if output_path is None:
        output_path = f"Dynamics_NAV_Audit_Journals_{len(df_financial)}_Enterprise.csv"

    df_audit.to_csv(output_path, index=False)
    print("Audit journals dataset generated successfully!")
    return df_audit


def validate_dataset(df_financial: pd.DataFrame, df_audit: pd.DataFrame) -> None:
    """Run basic consistency checks to make deployment safer."""
    if len(df_financial) == 0:
        raise ValueError("Financial dataset is empty.")
    if df_financial["Document_No"].nunique() != len(df_financial):
        raise ValueError("Duplicate Document_No values detected.")

    amount_check = (df_financial["Amount"] * df_financial["FX_Rate"]).round(2)
    if not amount_check.equals(df_financial["Amount_Group_Currency"]):
        raise ValueError("Amount_Group_Currency mismatch detected.")

    interco = df_financial[df_financial["Intercompany_Flag"] == 1]
    if (interco["Intercompany_To"] == "").any():
        raise ValueError("Intercompany rows missing Intercompany_To.")

    if df_audit["Document_No"].isin(df_financial["Document_No"]).mean() < 1:
        raise ValueError("Audit contains unknown Document_No values.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Dynamics NAV synthetic financial and audit datasets.")
    parser.add_argument(
        "--rows",
        type=int,
        default=TOTAL_ROWS,
        help=f"Number of financial rows to generate (default: {TOTAL_ROWS}).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for deterministic generation (default: 42).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rows <= 0:
        raise ValueError("--rows must be a positive integer.")

    np.random.seed(args.seed)

    df_financial = generate_financial_dataset(total_rows=args.rows)
    df_audit = generate_audit_journals(df_financial)
    validate_dataset(df_financial, df_audit)
    print("Validation checks passed.")


if __name__ == "__main__":
    main()
