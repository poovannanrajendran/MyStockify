import requests
from bs4 import BeautifulSoup
import pandas as pd
from forex_python.converter import CurrencyRates
from datetime import datetime

# List of stocks with Google Finance tickers
data = [
    {"isin": "CH0038863350", "ticker": "SWX:NESN", "name": "Nestle"},
    {"isin": "DE000A1EWWW0", "ticker": "FRA:ADS", "name": "Adidas"},
    {"isin": "GB0005603997", "ticker": "LON:LGEN", "name": "Legal & General"},
    # Add more tickers as needed
]

# Function to scrape stock price and currency from Google Finance
def get_stock_price(ticker):
    try:
        # URL for Google Finance stock page
        url = f"https://www.google.com/finance/quote/{ticker}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve data for {ticker}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scraping the stock price
        price_tag = soup.find('div', class_='YMlKec fxKbKc')
        if not price_tag:
            raise ValueError(f"Could not find stock price for {ticker}")
        price = float(price_tag.text.replace(',', '').replace('£', '').replace('$', '').replace('€', ''))

        # Determine the currency symbol from the price tag
        currency_symbol = price_tag.text[0]  # First character is usually the currency symbol
        currency_map = {'£': 'GBP', '$': 'USD', '€': 'EUR'}
        currency = currency_map.get(currency_symbol, 'USD')  # Default to USD if not found

        return price, currency
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

# Function to get exchange rate
def get_exchange_rate(currency):
    c = CurrencyRates()
    try:
        rate = c.get_rate(currency, 'GBP')
    except Exception as e:
        print(f"Error fetching exchange rate for {currency}: {e}")
        rate = 1  # Default to 1 if there's an issue
    return rate

# Initialize list for storing results
results = []

# Fetch stock price and currency, and calculate value in GBP
for stock in data:
    price, currency = get_stock_price(stock['ticker'])
    if price is not None and currency is not None:
        exch_rate = get_exchange_rate(currency)
        value_in_gbp = price * exch_rate
        results.append({
            "isin": stock['isin'],
            "ticker": stock['ticker'],
            "name": stock['name'],
            "datetime": datetime.now(),
            "price": price,
            "currency": currency,
            "exchangerate_to_gbp": exch_rate,
            "value_in_gbp": value_in_gbp
        })

# Convert to DataFrame
df = pd.DataFrame(results)

# Write to CSV
df.to_csv("google_finance_stock_prices.csv", index=False)

print("Stock prices saved to 'google_finance_stock_prices.csv'")
