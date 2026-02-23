/* Dynamics NAV Analytics Warehouse Schema (SQL Server compatible) */

-- 1) Dimension tables
CREATE TABLE dbo.DimDate (
    DateKey        INT         NOT NULL PRIMARY KEY,
    [Date]         DATE        NOT NULL,
    [Year]         INT         NOT NULL,
    [Quarter]      VARCHAR(2)  NOT NULL,
    [Month]        INT         NOT NULL,
    [MonthName]    VARCHAR(20) NOT NULL
);

CREATE TABLE dbo.DimAccount (
    AccountKey     INT IDENTITY(1,1) PRIMARY KEY,
    Account_No     VARCHAR(20)  NOT NULL,
    Account_Name   VARCHAR(200) NOT NULL,
    Category       VARCHAR(50)  NOT NULL
);

CREATE TABLE dbo.DimDepartment (
    DepartmentKey  INT IDENTITY(1,1) PRIMARY KEY,
    Department     VARCHAR(100) NOT NULL,
    Cost_Center    VARCHAR(100) NOT NULL
);

CREATE TABLE dbo.DimSubsidiary (
    SubsidiaryKey  INT IDENTITY(1,1) PRIMARY KEY,
    Subsidiary     VARCHAR(100) NOT NULL
);

-- 2) Fact tables
CREATE TABLE dbo.FactFinancial (
    Document_No             VARCHAR(30)  NOT NULL PRIMARY KEY,
    DateKey                 INT          NOT NULL,
    SubsidiaryKey           INT          NOT NULL,
    DepartmentKey           INT          NOT NULL,
    AccountKey              INT          NOT NULL,
    Amount                  DECIMAL(18,2) NOT NULL,
    Amount_Group_Currency   DECIMAL(18,2) NOT NULL,
    Approved                BIT          NOT NULL,
    [Status]                VARCHAR(20)  NOT NULL,
    Intercompany_Flag       BIT          NOT NULL,
    Currency                VARCHAR(10)  NULL,
    FX_Rate                 DECIMAL(18,6) NULL,
    Transaction_Type        VARCHAR(100) NULL,
    CONSTRAINT FK_FactFinancial_Date FOREIGN KEY (DateKey) REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactFinancial_Subsidiary FOREIGN KEY (SubsidiaryKey) REFERENCES dbo.DimSubsidiary(SubsidiaryKey),
    CONSTRAINT FK_FactFinancial_Department FOREIGN KEY (DepartmentKey) REFERENCES dbo.DimDepartment(DepartmentKey),
    CONSTRAINT FK_FactFinancial_Account FOREIGN KEY (AccountKey) REFERENCES dbo.DimAccount(AccountKey)
);

CREATE TABLE dbo.FactAudit (
    Audit_ID                 INT          NOT NULL PRIMARY KEY,
    Document_No              VARCHAR(30)  NOT NULL,
    DateKey                  INT          NULL,
    SubsidiaryKey            INT          NULL,
    DepartmentKey            INT          NULL,
    Action_Type              VARCHAR(50)  NOT NULL,
    New_Amount               DECIMAL(18,2) NULL,
    Performed_On             DATE         NULL,
    CONSTRAINT FK_FactAudit_Document FOREIGN KEY (Document_No) REFERENCES dbo.FactFinancial(Document_No)
);

-- 3) Helpful indexes for scale
CREATE INDEX IX_FactFinancial_DateKey ON dbo.FactFinancial(DateKey);
CREATE INDEX IX_FactFinancial_AccountKey ON dbo.FactFinancial(AccountKey);
CREATE INDEX IX_FactFinancial_SubsidiaryKey ON dbo.FactFinancial(SubsidiaryKey);
CREATE INDEX IX_FactAudit_DocumentNo ON dbo.FactAudit(Document_No);

-- 4) Ratio analysis view
CREATE VIEW dbo.vw_Financial_Ratio_Base
AS
SELECT
    d.[Year],
    d.[Month],
    s.Subsidiary,
    SUM(CASE WHEN a.Category = 'Revenue' THEN f.Amount_Group_Currency ELSE 0 END) AS Revenue,
    SUM(CASE WHEN a.Category = 'COGS' THEN ABS(f.Amount_Group_Currency) ELSE 0 END) AS COGS,
    SUM(CASE WHEN a.Category = 'OPEX' THEN ABS(f.Amount_Group_Currency) ELSE 0 END) AS OPEX,
    SUM(CASE WHEN f.Intercompany_Flag = 1 THEN ABS(f.Amount_Group_Currency) ELSE 0 END) AS IntercompanyVolume,
    COUNT_BIG(*) AS TransactionCount
FROM dbo.FactFinancial f
JOIN dbo.DimDate d ON f.DateKey = d.DateKey
JOIN dbo.DimAccount a ON f.AccountKey = a.AccountKey
JOIN dbo.DimSubsidiary s ON f.SubsidiaryKey = s.SubsidiaryKey
GROUP BY d.[Year], d.[Month], s.Subsidiary;
GO
