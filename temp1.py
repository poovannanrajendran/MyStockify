import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sample data for illustration
data = {
    'Ticker': ['ABBV', 'ADS', 'AMD', 'AGNC', 'GOOGL', 'AMZN', 'AXP', 'AAPL'],
    'TotalShares': [0.457, 0.0697, 0.442, 0.451, 0.539, 0.509, 0.385, 1.419],
    'AvgBuyPrice': [172.25, 174.76, 164.75, 9.74, 171.35, 181.99, 231.44, 212.97],
    'CurrentMarketPrice': [186.54, 222.60, 157.90, 10.38, 164.09, 189.07, 270.74, 236.48],
    'ProfitLossGBP': [2.67, -2.43, -1.18, 0.11, -1.84, 4.19, 8.18, 50.79],
    'ProfitLossPercentage': [8.29, -23.37, -4.16, 6.57, -4.24, 3.89, 16.98, 24.44],
    'TotalBuyPriceGBP': [63.05, 10.39, 55.04, 3.49, 69.97, 69.97, 72.07, 207.83],
    'TotalCurrentMarketPriceGBP': [65.71, 7.96, 53.86, 3.60, 68.13, 74.16, 80.25, 258.62],
}
portfolio_df = pd.DataFrame(data)

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
