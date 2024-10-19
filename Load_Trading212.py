import pyodbc
import pandas as pd
from datetime import datetime
import settings  # Import settings from settings.py

# Function to connect to SQL Server
def connect_to_sql_server():
    conn_str = (
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
    print(f"Filename: {file_name}, Batch ID: {batch_id}")
    conn.commit()
    return batch_id

# Function to insert data into LandingData_Staging (all VARCHAR columns except BatchID)
def insert_staging_data(conn, df, batch_id):
    cursor = conn.cursor()

    # Counter to track rows inserted
    row_count = 0

    # Convert all values in the DataFrame to string
    transactions_df = df.astype(str)

    # Truncate the table before loading new data
    cursor.execute("TRUNCATE TABLE LandingData_Staging")
    conn.commit()

    for index, row in transactions_df.iterrows():
        try:
            # Insert statement with all columns
            cursor.execute("""
                INSERT INTO LandingData_Staging (
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

            # Increment row counter
            row_count += 1

            # Commit every 100 rows
            if row_count % 100 == 0:
                conn.commit()
                print(f"Committed after {row_count} rows")

        except pyodbc.Error as e:
            print(f"Error inserting row {index}: {e}")
            print(row)

    # Final commit for any remaining rows
    if row_count % 100 != 0:
        conn.commit()
        print(f"Final commit after {row_count} rows")

    conn.commit()
    # Execute the stored procedure
    try:
        cursor.execute("{CALL [dbo].[spCleanup_LandingData_Staging]}")
        conn.commit()  # Commit the transaction if needed
        print("Stored procedure executed successfully.")
    except pyodbc.Error as e:
        print(f"Error executing stored procedure: {e}")

# Function to execute the stored procedure after staging data is loaded
def execute_stored_procedure(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("{CALL [dbo].[spLoadFromStaging]}")
        conn.commit()
        print("Stored procedure executed successfully.")
    except pyodbc.Error as e:
        print(f"Error executing stored procedure: {e}")

# Load the CSV file
def load_csv(file_path):
    return pd.read_csv(file_path)

# Main processing function
def process_file(file_path):
    # Connect to SQL Server
    conn = connect_to_sql_server()
    
    # Load CSV data
    df = load_csv(file_path)
    
    # Insert Batch and get BatchID
    file_name = file_path.split('/')[-1]
    batch_id = insert_batch(conn, file_name)
    
    # Insert data into LandingData_Staging table
    insert_staging_data(conn, df, batch_id)

    # Execute the stored procedure to process staging data
    execute_stored_procedure(conn)

    # Close the connection
    conn.close()

# Example usage:
file_path = settings.filepath + 'from_2024-01-25_to_2024-10-11_MTcyODY3NDAyMjMyNw.csv'

# Run the process
process_file(file_path)
