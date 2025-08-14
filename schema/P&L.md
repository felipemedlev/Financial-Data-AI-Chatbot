# Profit & Loss (P&L) Data Schema

## Overview
This schema describes the financial data structure loaded from the P&L_ChatBot.xlsx file, containing monthly financial information from January 2022 to July 2025 for various companies across different countries and currencies.

## Columns
- **Year**: Financial year (2022-2025)
- **Country**: Country of operation (e.g., "Chile", "Peru", "Colombia", "Argentina", "Brazil")
- **Currency**: Currency of the financial data ("USD" or "Moneda Local")
- **CompanyName**: Company name (see Company Mappings below)
- **Scenario**: Type of data ("REAL" for actual financials, "PPTO" for budget/forecast)
- **Account**: Financial account category (see Account Categories below)
- **Month**: Month of the financial data ("January" through "December")
- **Value**: Financial value for the specific account in the specified currency
- **Sheet**: Source sheet identifier (USD_REAL, USD_PPTO, MONEDALOCAL_REAL, MONEDALOCAL_PPTO)

## Company Mappings
- "Total Retail" = "Falabella Retail"
- "Total Sodimac" = "Sodimac"
- "Total Tottus" = "Tottus"

## Account Categories
The P&L structure follows this hierarchy:
- **Margen de Explotacion** (Operating Margin)
- **gavPrimo** (Expenditure)
- **Resultado No Operacional** (Non-Operating Result)
- **Ajustes Holding** (Holding Adjustments)
- **Impuestos** (Taxes)
- **Resultado** / **Utilidad** (Final Result/Profit - calculated as the sum of all above components)

## Currency Information
- **Dolares** = USD (United States Dollars)
- **Moneda Local** = Local currency of each country

## Time Period
- Data available from January 2022 to July 2025
- Monthly granularity

## Data Sources
The data comes from 4 sheets in the Excel file:
1. **USD_REAL**: Actual financials in USD
2. **USD_PPTO**: Budget (presupuesto) financials in USD
3. **MONEDALOCAL_REAL**: Actual financials in local currency
4. **MONEDALOCAL_PPTO**: Budget (presupuesto) financials in local currency

## Sample Queries
- Compare actual vs budget performance: Filter by Scenario
- Analyze currency impact: Compare USD vs Moneda Local for the same companies
- Track company performance over time: Group by CompanyName and Year
- Calculate profit margins: Use Account categories to compute ratios
- Geographic analysis: Group by Country