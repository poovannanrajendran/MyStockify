import pyodbc
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import settings  # Import settings from settings.py

# Cache file path (persistent storage on disk)
CACHE_FILE_PATH = 'portfolio_cache.1csv'

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

# Fetch data with caching logic
portfolio_df = get_data_with_cache(fetch_live_data)

# Create Dash app
app = dash.Dash(__name__)
app.title = "Portfolio Dashboard"

# Layout for the dashboard
app.layout = html.Div([
    html.H1("Stock Portfolio Dashboard"),

    # Portfolio Overview Cards
    html.Div([
        html.Div([
            html.H4("Total Investment"),
            html.P(f"£{portfolio_df['TotalBuyPriceGBP'].sum():,.2f}")
        ], className='card'),
        html.Div([
            html.H4("Current Market Value"),
            html.P(f"£{portfolio_df['TotalCurrentMarketPriceGBP'].sum():,.2f}")
        ], className='card'),
        html.Div([
            html.H4("Total Profit/Loss"),
            html.P(f"£{portfolio_df['ProfitLossGBP'].sum():,.2f} "
                   f"({(portfolio_df['ProfitLossGBP'].sum() / portfolio_df['TotalBuyPriceGBP'].sum()) * 100:.2f}%)")
        ], className='card'),
    ], className='card-container'),

    # Profit/Loss Distribution by Stock
    html.Div(
        dcc.Graph(
            id='profit-loss-distribution',
            figure=px.bar(portfolio_df, x='Ticker', y='ProfitLossGBP', title="Profit/Loss Distribution by Stock")
        ), className='graph-container'
    ),

    # Portfolio Allocation by Stock
    html.Div(
        dcc.Graph(
            id='portfolio-allocation',
            figure=px.pie(portfolio_df, values='TotalCurrentMarketPriceGBP', names='Ticker',
                          title="Portfolio Allocation by Stock")
        ), className='graph-container'
    ),

    # Full Performance Breakdown Table
    html.H2("Full Performance Breakdown"),
    html.Div(
        dash_table.DataTable(
            id='portfolio-table',
            columns=[{"name": col, "id": col} for col in portfolio_df.columns],
            data=portfolio_df.sort_values(by='ProfitLossGBP', ascending=False).to_dict('records'),
            sort_action='native'
        ), className='dash-table-container'
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
