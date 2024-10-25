import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
from settings import API_KEY  # Import API key from settings.py
import time

# Trading212 API URL
BASE_URL = "https://live.trading212.com/api/v0/"
headers = {
    "Authorization": API_KEY
}

# Initialize Dash app
app = dash.Dash(__name__)

# Data Fetching Functions with delay

def fetch_account_info():
    try:
        print("Fetching account info...")
        response = requests.get(f"{BASE_URL}equity/account/info", headers=headers)
        time.sleep(1)  # Add delay to avoid rate limiting
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error fetching account info: {response.status_code} - {response.text}")
            return None

        account_info = response.json()
        print("Account info retrieved:", account_info)
        return account_info
    except requests.exceptions.RequestException as e:
        print("Request error while fetching account info:", e)
        return None
    except requests.JSONDecodeError:
        print("Error: Response is not in JSON format.")
        print(response.text)  # Print response text for debugging
        return None

def fetch_portfolio():
    try:
        print("Fetching portfolio data...")
        response = requests.get(f"{BASE_URL}equity/portfolio", headers=headers)
        time.sleep(1)  # Add delay to avoid rate limiting
        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"Error fetching portfolio data: {response.status_code} - {response.text}")
            return pd.DataFrame()  # Return empty DataFrame on error

        portfolio_data = response.json()
        print("Portfolio data retrieved:", portfolio_data)
        return pd.DataFrame(portfolio_data)
    except requests.exceptions.RequestException as e:
        print("Request error while fetching portfolio data:", e)
        return pd.DataFrame()
    except requests.JSONDecodeError:
        print("Error: Portfolio response is not in JSON format.")
        print(response.text)  # Print response text for debugging
        return pd.DataFrame()

def fetch_historical_orders():
    try:
        print("Fetching historical orders...")
        response = requests.get(f"{BASE_URL}history/orders", headers=headers)
        time.sleep(1)  # Add delay to avoid rate limiting
        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"Error fetching historical orders: {response.status_code} - {response.text}")
            return pd.DataFrame()

        orders_data = response.json()
        print("Historical orders data retrieved:", orders_data)
        return pd.DataFrame(orders_data["items"])
    except requests.exceptions.RequestException as e:
        print("Request error while fetching historical orders:", e)
        return pd.DataFrame()
    except requests.JSONDecodeError:
        print("Error: Historical orders response is not in JSON format.")
        print(response.text)  # Print response text for debugging
        return pd.DataFrame()

# Fetch and prepare data
print("Starting data retrieval...")
account_info = fetch_account_info()
portfolio_df = fetch_portfolio()
historical_orders_df = fetch_historical_orders()

# Check data after fetching
if account_info is None:
    print("Failed to retrieve account information.")
else:
    print("Account info:", account_info)

if portfolio_df.empty:
    print("Portfolio data is empty.")
else:
    print("Portfolio data:", portfolio_df.head())

if historical_orders_df.empty:
    print("Historical orders data is empty.")
else:
    print("Historical orders data:", historical_orders_df.head())

# Dashboard Layout
app.layout = html.Div([
    html.H1("Trading212 Portfolio Dashboard"),
    html.Div([
        html.H2("Account Summary"),
        html.P(f"Currency: {account_info['currencyCode'] if account_info else 'N/A'}"),
        #html.P(f"Total Cash: {account_info['total'] if account_info else 'N/A'}"),
        html.P(f"Total Cash: {account_info.get('total', 'N/A') if account_info else 'N/A'}"),

    ]),
    html.Div([
        dcc.Graph(id='portfolio-performance'),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[{'label': ticker, 'value': ticker} for ticker in portfolio_df['ticker'].unique()] if not portfolio_df.empty else [],
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
    # Verbose output
    print("Updating portfolio performance graph...")
    print(f"Selected ticker: {selected_ticker}")

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
    print("Updating drilldown chart...")
    print(f"Selected ticker for drilldown: {selected_ticker}")

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
    print("Running Dash app...")
    app.run_server(debug=True)
