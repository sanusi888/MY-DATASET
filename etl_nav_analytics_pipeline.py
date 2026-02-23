"""ETL pipeline for Dynamics NAV synthetic financial + audit datasets.

Outputs a scalable analytics model with:
- DimDate
- DimAccount
- DimDepartment
- DimSubsidiary
- FactFinancial
- FactAudit
- KpiMonthly (pre-aggregated ratio-support dataset)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd


REQUIRED_FINANCIAL_COLUMNS = {
    "Posting_Date",
    "Subsidiary",
    "Department",
    "Cost_Center",
    "Account_No",
    "Account_Name",
    "Category",
    "Amount",
    "Amount_Group_Currency",
    "Document_No",
    "Approved",
    "Status",
    "Intercompany_Flag",
}

REQUIRED_AUDIT_COLUMNS = {
    "Audit_ID",
    "Document_No",
    "Action_Type",
    "Performed_On",
    "New_Amount",
}


class NavEtlPipeline:
    def __init__(self, financial_csv: Path, audit_csv: Path, output_dir: Path) -> None:
        self.financial_csv = financial_csv
        self.audit_csv = audit_csv
        self.output_dir = output_dir
        self.model_dir = output_dir / "model"
        self.model_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_columns(df: pd.DataFrame, required_cols: Iterable[str], label: str) -> None:
        missing = sorted(set(required_cols) - set(df.columns))
        if missing:
            raise ValueError(f"{label} is missing required columns: {missing}")

    @staticmethod
    def _load_csv(path: Path, parse_dates: List[str]) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        return pd.read_csv(path, parse_dates=parse_dates)

    def extract(self) -> Dict[str, pd.DataFrame]:
        financial = self._load_csv(self.financial_csv, ["Posting_Date", "Expected_Cashflow_Date", "Due_Date"])
        audit = self._load_csv(self.audit_csv, ["Performed_On"])

        self._validate_columns(financial, REQUIRED_FINANCIAL_COLUMNS, "Financial CSV")
        self._validate_columns(audit, REQUIRED_AUDIT_COLUMNS, "Audit CSV")
        return {"financial": financial, "audit": audit}

    @staticmethod
    def _normalize_financial_types(df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        normalized["Amount"] = pd.to_numeric(normalized["Amount"], errors="coerce").fillna(0.0)
        normalized["Amount_Group_Currency"] = pd.to_numeric(
            normalized["Amount_Group_Currency"], errors="coerce"
        ).fillna(0.0)
        normalized["Approved"] = pd.to_numeric(normalized["Approved"], errors="coerce").fillna(0).astype(int)
        normalized["Intercompany_Flag"] = (
            pd.to_numeric(normalized["Intercompany_Flag"], errors="coerce").fillna(0).astype(int)
        )
        normalized["Document_No"] = normalized["Document_No"].astype(str)
        normalized["Posting_Date"] = pd.to_datetime(normalized["Posting_Date"])
        return normalized

    @staticmethod
    def _normalize_audit_types(df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        normalized["Audit_ID"] = pd.to_numeric(normalized["Audit_ID"], errors="coerce").fillna(0).astype(int)
        normalized["New_Amount"] = pd.to_numeric(normalized["New_Amount"], errors="coerce").fillna(0.0)
        normalized["Document_No"] = normalized["Document_No"].astype(str)
        normalized["Performed_On"] = pd.to_datetime(normalized["Performed_On"])
        return normalized

    @staticmethod
    def _build_dim_date(financial: pd.DataFrame) -> pd.DataFrame:
        min_date = financial["Posting_Date"].min()
        max_date = financial["Posting_Date"].max()
        dim_date = pd.DataFrame({"Date": pd.date_range(min_date, max_date, freq="D")})
        dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
        dim_date["Year"] = dim_date["Date"].dt.year
        dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
        dim_date["Month"] = dim_date["Date"].dt.month
        dim_date["MonthName"] = dim_date["Date"].dt.month_name()
        return dim_date[["DateKey", "Date", "Year", "Quarter", "Month", "MonthName"]]

    @staticmethod
    def _build_dimension(df: pd.DataFrame, columns: List[str], key_name: str) -> pd.DataFrame:
        dim = df[columns].drop_duplicates().reset_index(drop=True)
        dim[key_name] = dim.index + 1
        return dim[[key_name] + columns]

    def transform(self, extracted: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        financial = self._normalize_financial_types(extracted["financial"])
        audit = self._normalize_audit_types(extracted["audit"])

        dim_date = self._build_dim_date(financial)
        dim_account = self._build_dimension(financial, ["Account_No", "Account_Name", "Category"], "AccountKey")
        dim_department = self._build_dimension(financial, ["Department", "Cost_Center"], "DepartmentKey")
        dim_subsidiary = self._build_dimension(financial, ["Subsidiary"], "SubsidiaryKey")

        financial = financial.merge(dim_account, on=["Account_No", "Account_Name", "Category"], how="left")
        financial = financial.merge(dim_department, on=["Department", "Cost_Center"], how="left")
        financial = financial.merge(dim_subsidiary, on=["Subsidiary"], how="left")

        financial["DateKey"] = financial["Posting_Date"].dt.strftime("%Y%m%d").astype(int)

        fact_financial = financial[
            [
                "Document_No",
                "DateKey",
                "SubsidiaryKey",
                "DepartmentKey",
                "AccountKey",
                "Amount",
                "Amount_Group_Currency",
                "Approved",
                "Status",
                "Intercompany_Flag",
                "Currency",
                "FX_Rate",
                "Transaction_Type",
            ]
        ].copy()

        doc_lookup = financial[["Document_No", "DateKey", "SubsidiaryKey", "DepartmentKey"]].drop_duplicates()
        fact_audit = audit.merge(doc_lookup, on="Document_No", how="left")
        fact_audit = fact_audit[
            [
                "Audit_ID",
                "Document_No",
                "DateKey",
                "SubsidiaryKey",
                "DepartmentKey",
                "Action_Type",
                "New_Amount",
                "Performed_On",
            ]
        ].copy()

        kpi_monthly = (
            financial.assign(YearMonth=financial["Posting_Date"].dt.to_period("M").astype(str))
            .groupby(["YearMonth", "Subsidiary", "Category"], as_index=False)
            .agg(Total_Amount=("Amount_Group_Currency", "sum"), Tx_Count=("Document_No", "count"))
        )

        return {
            "DimDate": dim_date,
            "DimAccount": dim_account,
            "DimDepartment": dim_department,
            "DimSubsidiary": dim_subsidiary,
            "FactFinancial": fact_financial,
            "FactAudit": fact_audit,
            "KpiMonthly": kpi_monthly,
        }

    def load(self, transformed: Dict[str, pd.DataFrame], output_format: str = "parquet") -> None:
        for name, df in transformed.items():
            if output_format == "csv":
                out_path = self.model_dir / f"{name}.csv"
                df.to_csv(out_path, index=False)
            else:
                out_path = self.model_dir / f"{name}.parquet"
                df.to_parquet(out_path, index=False)

    def run(self, output_format: str = "parquet") -> None:
        extracted = self.extract()
        transformed = self.transform(extracted)
        self.load(transformed, output_format=output_format)
        print(f"ETL completed. Model files saved in: {self.model_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NAV analytics ETL pipeline.")
    parser.add_argument(
        "--financial-csv",
        default="Dynamics_NAV_Financials_150K_Enterprise.csv",
        help="Path to financial CSV source.",
    )
    parser.add_argument(
        "--audit-csv",
        default="Dynamics_NAV_Audit_Journals_150K_Enterprise.csv",
        help="Path to audit CSV source.",
    )
    parser.add_argument(
        "--output-dir",
        default="analytics_output",
        help="Directory for dimensional model outputs.",
    )
    parser.add_argument(
        "--output-format",
        choices=["parquet", "csv"],
        default="parquet",
        help="Output format for analytics model tables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = NavEtlPipeline(Path(args.financial_csv), Path(args.audit_csv), Path(args.output_dir))
    pipeline.run(output_format=args.output_format)


if __name__ == "__main__":
    main()
