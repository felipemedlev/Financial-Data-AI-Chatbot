import pandas as pd

def load_financial_data(file_path='data/P&L_ChatBot.xlsx'):
    """
    Load financial data from Excel file and transform it into a queryable format.

    Parameters:
    file_path (str): Path to the Excel file

    Returns:
    pd.DataFrame: Transformed financial data with all sheets combined
    """
    # Define the column names
    column_names = [
        'Year', 'Country', 'Currency', 'CompanyName', 'Scenario', 'Account',
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December', 'FullYear'
    ]

    # Define sheet names
    sheet_names = ['USD_REAL', 'USD_PPTO', 'MONEDALOCAL_REAL', 'MONEDALOCAL_PPTO']

    # List to store processed dataframes
    dataframes = []

    # Process each sheet
    for sheet_name in sheet_names:
        # Read the sheet, skipping first 2 rows
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)

        # Assign column names
        df.columns = column_names

        # Drop the FullYear column
        df = df.drop(columns=['FullYear'])

        # Add a column to identify the sheet
        df['Sheet'] = sheet_name

        # Pivot the data to transform months into rows
        # Melt the dataframe to convert monthly columns to rows
        monthly_columns = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        df_melted = df.melt(
            id_vars=['Year', 'Country', 'Currency', 'CompanyName', 'Scenario', 'Account', 'Sheet'],
            value_vars=monthly_columns,
            var_name='Month',
            value_name='Value'
        )

        # Add the processed dataframe to our list
        dataframes.append(df_melted)

    # Combine all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)

    return combined_df

# Example usage
if __name__ == "__main__":
    # Load the data
    financial_data = load_financial_data()
    # print(financial_data.head(10))
    # print(f"Total rows: {len(financial_data)}")
    # print(f"Columns: {list(financial_data.columns)}")

    df = financial_data.copy()
    company_name = "Total Retail"
    month_to_analyze = "March"
    year_to_analyze = 2025

    # Define the expected companies for "Total Retail" based on the schema
    falabella_retail_companies = [
        "Total Retail Chile",
        "Total Retail Argentina",
        "Total Retail Peru",
        "Total Retail Colombia",
    ]

    # Filter data for the specified month and year
    march_2025_data = df[
        (df["Month"] == month_to_analyze)
        & (df["Year"] == year_to_analyze)
        & (df["CompanyName"].isin(falabella_retail_companies))
        & (df["Account"] == "Ingresos de Explotacion") # Assuming "revenue" maps to "Ingresos de Explotacion"
    ]

    # Filter data for the previous year (March 2024)
    march_2024_data = df[
        (df["Month"] == month_to_analyze)
        & (df["Year"] == year_to_analyze - 1)
        & (df["CompanyName"].isin(falabella_retail_companies))
        & (df["Account"] == "Ingresos de Explotacion")
    ]

    # Filter data for budget in March 2025
    march_2025_budget_data = df[
        (df["Month"] == month_to_analyze)
        & (df["Year"] == year_to_analyze)
        & (df["CompanyName"].isin(falabella_retail_companies))
        & (df["Scenario"] == "Presupuesto")
        & (df["Account"] == "Ingresos de Explotacion")
    ]

    # Aggregate revenue for March 2025
    march_2025_revenue = march_2025_data["Value"].sum()

    # Aggregate revenue for March 2024
    march_2024_revenue = march_2024_data["Value"].sum()

    # Aggregate budget revenue for March 2025
    march_2025_budget_revenue = march_2025_budget_data["Value"].sum()

    # Calculate variances
    variance_vs_last_year = march_2025_revenue - march_2024_revenue
    variance_vs_budget = march_2025_revenue - march_2025_budget_revenue

    # Format the output string
    output = (
        f"Falabella Retail Revenue:\n"
        f"- March {year_to_analyze}: {march_2025_revenue:,.2f}\n"
        f"- March {year_to_analyze - 1}: {march_2024_revenue:,.2f}\n"
        f"- Budget for March {year_to_analyze}: {march_2025_budget_revenue:,.2f}\n"
        f"Variance vs Last Year (March {year_to_analyze} vs March {year_to_analyze - 1}): {variance_vs_last_year:,.2f}\n"
        f"Variance vs Budget (March {year_to_analyze}): {variance_vs_budget:,.2f}"
    )
    print(output)
