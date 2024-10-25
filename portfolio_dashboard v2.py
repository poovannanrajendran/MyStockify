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

# Cache file path
CACHE_FILE_PATH = 'portfolio_cache.csv'

# Flag to force live data fetch
fetch_live_data = 1

# Function to connect to SQL Server
def connect_to_sql_server():
    conn_str = (
        f"DRIVER={{SQL Server}};"
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
    portfolio_df = pd.read_sql(query, conn)
    conn.close()
    return portfolio_df

# Function to retrieve transaction details for a specific stock from SQL Server
def get_transaction_details(ticker):
    conn = connect_to_sql_server()
    query = f"""
    SELECT 
        ID, BatchID, Action, Time, ISIN, Ticker, Name, NoOfShares, PricePerShare, TotalAmount, CurrencyTotal, Notes, 
        Currency, BuyAmount, ExchangeRate, BuyAmountGBP
    FROM 
        LatestBuySellTransactions
    WHERE 
        Ticker = '{ticker}'
    """
    transaction_df = pd.read_sql(query, conn)
    conn.close()
    return transaction_df

# Function to manage cache and fetch data
def get_data_with_cache(fetch_live_data=0):
    if fetch_live_data == 1 or not os.path.exists(CACHE_FILE_PATH):
        portfolio_df = get_portfolio_data()
        portfolio_df.to_csv(CACHE_FILE_PATH, index=False)
    else:
        portfolio_df = pd.read_csv(CACHE_FILE_PATH)
    return portfolio_df

# Modularized components
def create_overview_cards(portfolio_df):
    total_investment = f"£{portfolio_df['TotalBuyPriceGBP'].sum():,.2f}"
    current_market_value = f"£{portfolio_df['TotalCurrentMarketPriceGBP'].sum():,.2f}"
    total_profit_loss = f"£{portfolio_df['ProfitLossGBP'].sum():,.2f}"
    profit_loss_percentage = f"({(portfolio_df['ProfitLossGBP'].sum() / portfolio_df['TotalBuyPriceGBP'].sum()) * 100:.2f}%)"
    
    return html.Div([
        html.Div([html.H4("Total Investment"), html.P(total_investment)], className='card'),
        html.Div([html.H4("Current Market Value"), html.P(current_market_value)], className='card'),
        html.Div([html.H4("Total Profit/Loss"), html.P(f"{total_profit_loss} {profit_loss_percentage}")], className='card'),
    ], className='card-container')

def create_profit_loss_chart(portfolio_df):
    return dcc.Graph(
        id='profit-loss-distribution',
        figure=px.bar(portfolio_df, x='Ticker', y='ProfitLossGBP', title="Profit/Loss Distribution by Stock"),
        className='graph-container'
    )

def create_portfolio_allocation_chart(portfolio_df):
    return dcc.Graph(
        id='portfolio-allocation',
        figure=px.pie(portfolio_df, values='TotalCurrentMarketPriceGBP', names='Ticker', title="Portfolio Allocation by Stock"),
        className='graph-container'
    )

def create_performance_table(portfolio_df):
    return html.Div([
        html.H2("Full Performance Breakdown"),
        dash_table.DataTable(
            id='portfolio-table',
            columns=[{"name": col, "id": col} for col in portfolio_df.columns],
            data=portfolio_df.sort_values(by='ProfitLossGBP', ascending=False).to_dict('records'),
            sort_action='native'
        )
    ], className='dash-table-container')

# Main Dashboard Layout
app = dash.Dash(__name__)
app.title = "Portfolio Dashboard"

portfolio_df = get_data_with_cache(fetch_live_data)

app.layout = html.Div([
    html.H1("Stock Portfolio Dashboard"),
    create_overview_cards(portfolio_df),
    create_profit_loss_chart(portfolio_df),
    create_portfolio_allocation_chart(portfolio_df),
    create_performance_table(portfolio_df),
    html.Div(id='drilldown-output')  # Placeholder for drill-down output
])

# Drill-down callback for profit/loss distribution
@app.callback(
    Output('drilldown-output', 'children'),
    [Input('profit-loss-distribution', 'clickData')]
)
def display_drilldown(clickData):
    if clickData:
        selected_ticker = clickData['points'][0]['x']
        transaction_df = get_transaction_details(selected_ticker)
        
        # Table for transaction details for the selected stock
        return html.Div([
            html.H3(f"Transaction Details for {selected_ticker}"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in transaction_df.columns],
                data=transaction_df.to_dict('records'),
                sort_action='native',
                page_size=10
            )
        ])
    return html.P("Click on a stock bar to see transaction details.")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
