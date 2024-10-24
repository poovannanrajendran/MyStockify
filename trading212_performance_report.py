import pyodbc
import pandas as pd
import os
import settings  # Import settings from settings.py

# Cache file path (persistent storage on disk)
CACHE_FILE_PATH = 'portfolio_cache.csv'

# Flag to force live data fetch
fetch_live_data = 0

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

# Function to retrieve portfolio data from SQL Server
def get_portfolio_data():
    conn = connect_to_sql_server()
    query = """
    SELECT 
        Ticker, Name, TotalShares, AvgBuyPrice, CurrentMarketPrice, ProfitLossGBP, ProfitLossPercentage, 
        TotalBuyPriceGBP, TotalCurrentMarketPriceGBP
    FROM 
        LatestPortfolioSummary
    """
    # Read the data into a pandas DataFrame
    portfolio_df = pd.read_sql(query, conn)
    conn.close()
    return portfolio_df

# Function to load data from the cache file
def load_cache():
    if os.path.exists(CACHE_FILE_PATH):
        print("Loading data from cache...")
        return pd.read_csv(CACHE_FILE_PATH)
    else:
        print("No cache file found.")
        return None

# Function to save data to the cache file
def save_to_cache(portfolio_df):
    print("Saving data to cache...")
    portfolio_df.to_csv(CACHE_FILE_PATH, index=False)

# Function to manage cache and fetch data (live or cached)
def get_data_with_cache(fetch_live_data=0):
    # Check if we need to fetch live data
    if fetch_live_data == 1:
        print("Fetching live data from database...")
        portfolio_df = get_portfolio_data()
        save_to_cache(portfolio_df)  # Save the fetched data to the cache
        return portfolio_df

    # Attempt to load from cache
    portfolio_df = load_cache()

    # If no cache available, force live data fetch
    if portfolio_df is None:
        print("Cache unavailable. Fetching live data from database...")
        portfolio_df = get_portfolio_data()
        save_to_cache(portfolio_df)  # Save the fetched data to the cache
    
    return portfolio_df

# Function to generate the performance report
def generate_performance_report(portfolio_df):
    # 1. Portfolio Summary Metrics
    total_investment = portfolio_df['TotalBuyPriceGBP'].sum()
    current_market_value = portfolio_df['TotalCurrentMarketPriceGBP'].sum()
    total_profit_loss = portfolio_df['ProfitLossGBP'].sum()
    total_profit_loss_percentage = (total_profit_loss / total_investment) * 100

    # 2. Top and Worst Performers
    top_2_by_percentage = portfolio_df.nlargest(2, 'ProfitLossPercentage')
    top_2_by_value = portfolio_df.nlargest(2, 'ProfitLossGBP')

    worst_2_by_percentage = portfolio_df.nsmallest(2, 'ProfitLossPercentage')
    worst_2_by_value = portfolio_df.nsmallest(2, 'ProfitLossGBP')

    # 3. Portfolio Summary Report
    print("=== Portfolio Performance Report ===")
    print(f"Total Investment: £{total_investment:,.2f}")
    print(f"Current Market Value: £{current_market_value:,.2f}")
    print(f"Total Profit/Loss: £{total_profit_loss:,.2f} ({total_profit_loss_percentage:.2f}%)")

    # 4. Top Performers
    print("\n=== Top 2 Performers by Percentage ===")
    for index, stock in top_2_by_percentage.iterrows():
        print(f"Ticker: {stock['Ticker']}: {stock['Name']}")
        print(f"Profit/Loss Percentage: {stock['ProfitLossPercentage']:.2f}%")
        print(f"Profit/Loss Value: £{stock['ProfitLossGBP']:,.2f}")
        print(f"Current Market Value: £{stock['TotalCurrentMarketPriceGBP']:,.2f}")
        print(f"Investment Value: £{stock['TotalBuyPriceGBP']:,.2f}")
        print("")

    print("\n=== Top 2 Performers by Value ===")
    for index, stock in top_2_by_value.iterrows():
        print(f"Ticker: {stock['Ticker']}: {stock['Name']}")
        print(f"Profit/Loss Value: £{stock['ProfitLossGBP']:,.2f}")
        print(f"Profit/Loss Percentage: {stock['ProfitLossPercentage']:.2f}%")
        print(f"Current Market Value: £{stock['TotalCurrentMarketPriceGBP']:,.2f}")
        print(f"Investment Value: £{stock['TotalBuyPriceGBP']:,.2f}")
        print("")

    # 5. Worst Performers
    print("\n=== Worst 2 Performers by Percentage ===")
    for index, stock in worst_2_by_percentage.iterrows():
        print(f"Ticker: {stock['Ticker']}: {stock['Name']}")
        print(f"Profit/Loss Percentage: {stock['ProfitLossPercentage']:.2f}%")
        print(f"Profit/Loss Value: £{stock['ProfitLossGBP']:,.2f}")
        print(f"Current Market Value: £{stock['TotalCurrentMarketPriceGBP']:,.2f}")
        print(f"Investment Value: £{stock['TotalBuyPriceGBP']:,.2f}")
        print("")

    print("\n=== Worst 2 Performers by Value ===")
    for index, stock in worst_2_by_value.iterrows():
        print(f"Ticker: {stock['Ticker']}: {stock['Name']}")
        print(f"Profit/Loss Value: £{stock['ProfitLossGBP']:,.2f}")
        print(f"Profit/Loss Percentage: {stock['ProfitLossPercentage']:.2f}%")
        print(f"Current Market Value: £{stock['TotalCurrentMarketPriceGBP']:,.2f}")
        print(f"Investment Value: £{stock['TotalBuyPriceGBP']:,.2f}")
        print("")

    # 6. Full Performance Breakdown sorted by ProfitLossGBP
    print("\n=== Full Performance Breakdown by Stock (sorted by Profit/Loss) ===")
    sorted_portfolio = portfolio_df.sort_values(by='ProfitLossGBP', ascending=False)
    print(sorted_portfolio[['Ticker', 'Name', 'TotalShares', 'AvgBuyPrice', 'CurrentMarketPrice', 'ProfitLossGBP', 'ProfitLossPercentage']])

     # 7. Full Performance Breakdown sorted by ProfitLossGBP
    print("\n=== Full Performance Breakdown by Stock (sorted by Profit/Loss Percentage) ===")
    sorted_portfolio = portfolio_df.sort_values(by='ProfitLossPercentage', ascending=False)
    print(sorted_portfolio[['Ticker', 'Name', 'TotalShares', 'AvgBuyPrice', 'CurrentMarketPrice', 'ProfitLossGBP', 'ProfitLossPercentage']])

# Main function to retrieve data and generate the report
def main():
    # Fetch data (either cached or live)
    portfolio_df = get_data_with_cache(fetch_live_data=fetch_live_data)

    # Generate the performance report
    generate_performance_report(portfolio_df)

if __name__ == "__main__":
    main()
