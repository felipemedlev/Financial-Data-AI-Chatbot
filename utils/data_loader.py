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
    print(financial_data.head(10))
    print(f"Total rows: {len(financial_data)}")
    print(f"Columns: {list(financial_data.columns)}")