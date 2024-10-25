import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
from settings import API_KEY  # Import API key from settings.py

# Trading212 API URL
url = "https://live.trading212.com/api/v0/equity/portfolio"

# Use the API key from settings.py
headers = {
    "Authorization": API_KEY
}
# Initialize Dash app
app = dash.Dash(__name__)

# API Configuration
API_KEY = "API_KEY"
BASE_URL = "https://live.trading212.com/api/v0/"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Data Fetching Functions
def fetch_account_info():
    response = requests.get(f"{BASE_URL}equity/account/info", headers=headers)
    return response.json()

def fetch_portfolio():
    response = requests.get(f"{BASE_URL}equity/portfolio", headers=headers)
    return pd.DataFrame(response.json())

def fetch_historical_orders():
    response = requests.get(f"{BASE_URL}history/orders", headers=headers)
    return pd.DataFrame(response.json()["items"])

# Fetch and prepare data
account_info = fetch_account_info()
portfolio_df = fetch_portfolio()
historical_orders_df = fetch_historical_orders()

# Dashboard Layout
app.layout = html.Div([
    html.H1("Trading212 Portfolio Dashboard"),
    html.Div([
        html.H2("Account Summary"),
        html.P(f"Currency: {account_info['currencyCode']}"),
        html.P(f"Total Cash: {account_info['total']}"),
    ]),
    html.Div([
        dcc.Graph(id='portfolio-performance'),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[{'label': ticker, 'value': ticker} for ticker in portfolio_df['ticker'].unique()],
            placeholder="Select an asset",
        ),
    ]),
    dcc.Graph(id='drilldown-chart'),
])

# Callbacks for interactive components
@app.callback(
    Output('portfolio-performance', 'figure'),
    Input('ticker-dropdown', 'value')
)
def update_portfolio_performance(selected_ticker):
    # Filter data by selected ticker for drill-down
    data = portfolio_df if selected_ticker is None else portfolio_df[portfolio_df['ticker'] == selected_ticker]
    fig = go.Figure(
        data=[
            go.Pie(labels=data['ticker'], values=data['quantity'], hole=.3, title="Portfolio Distribution")
        ]
    )
    return fig

@app.callback(
    Output('drilldown-chart', 'figure'),
    Input('ticker-dropdown', 'value')
)
def update_drilldown_chart(selected_ticker):
    # Display detailed historical data for selected asset
    if selected_ticker:
        ticker_data = historical_orders_df[historical_orders_df['ticker'] == selected_ticker]
        fig = go.Figure([
            go.Scatter(x=ticker_data['dateExecuted'], y=ticker_data['fillResult'],
                       mode='lines+markers', name='Performance Over Time')
        ])
        return fig
    return go.Figure()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
