import pyodbc
import pandas as pd
from datetime import datetime
import settings  # Import settings from settings.py

# Function to connect to SQL Server
def connect_to_sql_server():
    conn_str = (
        #f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"DRIVER={{SQL Server}};"  # Use the existing 'SQL Server' driver
        f"SERVER={settings.server};"
        f"DATABASE={settings.database};"
        f"UID={settings.username};"
        f"PWD={settings.password}"
    )
    return pyodbc.connect(conn_str)

# Function to insert a new batch and return BatchID
def insert_batch(conn, file_name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Batch (FileName, ProcessedTimestamp) OUTPUT INSERTED.BatchID VALUES (?, GETDATE())", (file_name,))
    batch_id = cursor.fetchone()[0]
    print ("Filename = ", file_name, "ProcessedTimestamp = ", "Batch ID = ", batch_id)
    conn.commit()
    return batch_id

# Function to insert Landing Data (raw file data)
def insert_landing_data(conn, df, batch_id):
    cursor = conn.cursor()

    # List of numeric columns that need to be converted and cleaned
    numeric_columns = [
        'No. of shares', 'Price / share', 'Total', 'Withholding tax', 
        'Stamp duty reserve tax', 'Currency conversion fee'
    ]

    # Convert all numeric columns to floats, replacing invalid values with 0
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Insert each row into the LandingData table
    for index, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO LandingData (
                    BatchID, Action, Time, ISIN, Ticker, Name, NoOfShares, PricePerShare, 
                    CurrencyPriceShare, ExchangeRate, TotalAmount, CurrencyTotal, 
                    WithholdingTax, CurrencyWithholdingTax, StampDutyReserveTax, 
                    CurrencyStampDuty, Notes, TransactionID, CurrencyConversionFee, 
                    CurrencyConversionFeeCurrency
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                batch_id, row['Action'], row['Time'], row['ISIN'], row['Ticker'], row['Name'], 
                row['No. of shares'], row['Price / share'], row['Currency (Price / share)'], row['Exchange rate'],
                row['Total'], row['Currency (Total)'], row['Withholding tax'], row['Currency (Withholding tax)'], 
                row['Stamp duty reserve tax'], row['Currency (Stamp duty reserve tax)'], row['Notes'], 
                row['ID'], row['Currency conversion fee'], row['Currency (Currency conversion fee)']
            ))
        except pyodbc.Error as e:
            print(f"Error inserting row {index}: {e}")
            print(row)
    
    conn.commit()

# Function to insert deposit and interest transactions
def insert_deposit_interest(conn, df, batch_id):
    cursor = conn.cursor()
    deposits_df = df[df['Action'].isin(['Deposit', 'Interest on cash'])]  # Filter for deposits and interest
    for _, row in deposits_df.iterrows():
        cursor.execute("""
            INSERT INTO DepositInterest (BatchID, Action, Time, TotalAmount, CurrencyTotal, Notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (batch_id, row['Action'], row['Time'], row['Total'], row['Currency (Total)'], row['Notes']))
    print ("Inserted to Deposit Interest Table")
    conn.commit()

# Function to insert buy and sell transactions
def insert_buy_sell_transactions(conn, df, batch_id):
    cursor = conn.cursor()
    transactions_df = df[df['Action'].isin(['Market buy', 'Market sell'])]  # Filter for buy and sell transactions
    for _, row in transactions_df.iterrows():
        cursor.execute("""
            INSERT INTO BuySellTransactions (
                BatchID, Action, Time, ISIN, Ticker, Name, NoOfShares, PricePerShare, TotalAmount, CurrencyTotal, Notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (batch_id, row['Action'], row['Time'], row['ISIN'], row['Ticker'], row['Name'], row['No. of shares'], 
              row['Price / share'], row['Total'], row['Currency (Total)'], row['Notes']))
    print ("Inserted to buy_sell_transactions Table")
    conn.commit()

# Function to calculate and insert portfolio summary
def insert_portfolio_summary(conn, df, batch_id):
    cursor = conn.cursor()
    buy_transactions = df[df['Action'] == 'Market buy']
    portfolio = buy_transactions.groupby(['Ticker', 'Name']).agg(
        TotalShares=('No. of shares', 'sum'),
        AvgBuyPrice=('Price / share', 'mean')
    ).reset_index()

    for _, row in portfolio.iterrows():
        current_market_price = 100.0  # Placeholder for market price, can be updated dynamically
        profit_loss = (current_market_price - row['AvgBuyPrice']) * row['TotalShares']
        profit_loss_percentage = (profit_loss / (row['AvgBuyPrice'] * row['TotalShares'])) * 100
        
        cursor.execute("""
            INSERT INTO PortfolioSummary (
                BatchID, Ticker, Name, TotalShares, AvgBuyPrice, CurrentMarketPrice, ProfitLoss, ProfitLossPercentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (batch_id, row['Ticker'], row['Name'], row['TotalShares'], row['AvgBuyPrice'], 
              current_market_price, profit_loss, profit_loss_percentage))
    print ("Inserted to Portfolio Table")
    conn.commit()

# Load the CSV file
def load_csv(file_path):
    return pd.read_csv(file_path)

# Function to display 5 rows at a time and prompt for review
def review_data(df):
    # Expected data types for reference
    expected_data_types = {
        'BatchID': 'int',
        'Action': 'varchar(50)',
        'Time': 'datetime',
        'ISIN': 'varchar(50)',
        'Ticker': 'varchar(50)',
        'Name': 'varchar(255)',
        'No. of shares': 'float',
        'Price / share': 'float',
        'Currency (Price / share)': 'varchar(10)',
        'Exchange rate': 'varchar(50)',
        'Total': 'float',
        'Currency (Total)': 'varchar(10)',
        'Withholding tax': 'float',
        'Currency (Withholding tax)': 'varchar(10)',
        'Stamp duty reserve tax': 'float',
        'Currency (Stamp duty reserve tax)': 'varchar(10)',
        'Notes': 'text',
        'TransactionID': 'varchar(50)',
        'Currency conversion fee': 'float',
        'Currency (Currency conversion fee)': 'varchar(10)',
    }

    num_rows = len(df)
    for i in range(0, num_rows, 5):
        # Display 5 rows at a time
        chunk = df.iloc[i:i+5]
        print(f"\nReviewing rows {i+1} to {i+5}:")
        print(chunk)
        
        # Display expected data types
        print("\nExpected Data Types:")
        for column, dtype in expected_data_types.items():
            print(f"{column}: {dtype}")
        
        # Prompt user to continue or clean data
        cont = input("\nWould you like to continue with the next 5 rows? (y/n) If 'n', you can clean the data and rerun: ")
        if cont.lower() != 'y':
            print("Data review halted for cleanup. You can modify the data and rerun the process.")
            break



# Main processing function
def process_file(file_path):
    # Connect to SQL Server
    conn = connect_to_sql_server()
    
    # Load CSV data
    df = load_csv(file_path)
    
    # Review data in chunks of 5 rows
    review_data(df)

    # # Insert Batch and get BatchID
    # file_name = file_path.split('/')[-1]
    # batch_id = insert_batch(conn, file_name)
    
    # # Insert data into tables
    # insert_landing_data(conn, df, batch_id)
    # insert_deposit_interest(conn, df, batch_id)
    # insert_buy_sell_transactions(conn, df, batch_id)
    # insert_portfolio_summary(conn, df, batch_id)
    
    # Close the connection
    conn.close()

# Example usage:
file_path = settings.filepath + 'from_2024-01-25_to_2024-10-11_MTcyODY3NDAyMjMyNw.csv'

# Run the process
process_file(file_path)
