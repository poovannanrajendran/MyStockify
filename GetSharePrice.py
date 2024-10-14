import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
from datetime import datetime

# List of stocks with Nestle ticker adjusted for Yahoo Finance
data = [
    {"isin": "CH0038863350", "ticker": "NESN.SW", "name": "Nestle"},  # Adjusted ticker for Nestle
    {"isin": "DE000A1EWWW0", "ticker": "ADS", "name": "Adidas"},
    {"isin": "GB0005603997", "ticker": "LGEN", "name": "Legal & General"},
    {"isin": "GB0006436108", "ticker": "BRSC", "name": "BlackRock Smaller Cos Trust"},
    {"isin": "GG00B90J5Z95", "ticker": "TFIF", "name": "TwentyFour Income Fund"},
    {"isin": "GG00BJVDZ946", "ticker": "SMIF", "name": "TwentyFour Select Monthly Income Fund"},
    {"isin": "IE00B2NPKV68", "ticker": "SEMB", "name": "iShares J.P. Morgan USD EM Bond (Dist)"},
    {"isin": "IE00B2QWCY14", "ticker": "IDP6", "name": "iShares S&P Small Cap 600 (Dist)"},
    {"isin": "IE00B42WWV65", "ticker": "VGOV", "name": "Vanguard U.K. Gilt (Dist)"},
    {"isin": "IE00B48X4842", "ticker": "EMSD", "name": "SPDR MSCI Emerging Markets Small Cap (Acc)"},
    {"isin": "IE00B6S2Z822", "ticker": "UKDV", "name": "SPDR S&P UK Dividend Aristocrats (Dist)"},
    {"isin": "IE00BDD48R20", "ticker": "VUSC", "name": "Vanguard USD Corporate 1-3 Year Bond (Dist)"},
    {"isin": "IE00BF4RFH31", "ticker": "WLDS", "name": "iShares Msci World Small Cap (Acc)"},
    {"isin": "IE00BFMXXD54", "ticker": "VUAG", "name": "Vanguard S&P 500 (Acc)"},
    {"isin": "IE00BQZJBM26", "ticker": "DGSE", "name": "WisdomTree Emerging Markets SmallCap Dividend (Dist)"},
    {"isin": "IE00BZCQB185", "ticker": "NDIA", "name": "iShares MSCI India (Acc)"},
    {"isin": "LU0322253906", "ticker": "XXSC", "name": "Xtrackers MSCI Europe Small Cap (Acc)"},
    {"isin": "US00123Q1040", "ticker": "AGNC", "name": "AGNC Investment"},
    {"isin": "US00287Y1091", "ticker": "ABBV", "name": "AbbVie"},
    {"isin": "US0079031078", "ticker": "AMD", "name": "Advanced Micro Devices"},
    {"isin": "US0084921008", "ticker": "ADC", "name": "Agree Realty"},
    {"isin": "US02079K3059", "ticker": "GOOGL", "name": "Alphabet (Class A)"},
    {"isin": "US0231351067", "ticker": "AMZN", "name": "Amazon"},
    {"isin": "US0258161092", "ticker": "AXP", "name": "American Express"},
    {"isin": "US0378331005", "ticker": "AAPL", "name": "Apple"},
    {"isin": "US0423157058", "ticker": "ARR", "name": "ARMOUR Residential REIT"},
    {"isin": "US0605051046", "ticker": "BAC", "name": "Bank of America"},
    {"isin": "US0846701086", "ticker": "BRK.A", "name": "Berkshire Hathaway (Class A)"},
    {"isin": "US1912161007", "ticker": "KO", "name": "Coca-Cola"},
    {"isin": "US30303M1027", "ticker": "META", "name": "Meta Platforms"},
    {"isin": "US3765358789", "ticker": "GLAD", "name": "Gladstone Capital"},
    {"isin": "US4781601046", "ticker": "JNJ", "name": "Johnson & Johnson"},
    {"isin": "US5021751020", "ticker": "LTC", "name": "LTC Properties"},
    {"isin": "US5398301094", "ticker": "LMT", "name": "Lockheed Martin"},
    {"isin": "US56035L1044", "ticker": "MAIN", "name": "Main Street Capital"},
    {"isin": "US5949181045", "ticker": "MSFT", "name": "Microsoft"},
    {"isin": "US6311031081", "ticker": "NDAQ", "name": "Nasdaq"},
    {"isin": "US67066G1040", "ticker": "NVDA", "name": "Nvidia"},
    {"isin": "US7427181091", "ticker": "PG", "name": "Procter & Gamble"},
    {"isin": "US74348T1025", "ticker": "PSEC", "name": "Prospect Capital"},
    {"isin": "US7561091049", "ticker": "O", "name": "Realty Income"},
    {"isin": "US8305661055", "ticker": "SKX", "name": "Skechers USA"},
    {"isin": "US8334451098", "ticker": "SNOW", "name": "Snowflake"},
    {"isin": "US85254J1025", "ticker": "STAG", "name": "STAG Industrial"},
    {"isin": "US88160R1014", "ticker": "TSLA", "name": "Tesla"}
]


# Function to get stock price and currency
def get_stock_price(ticker, name):
    # Hardcode the price for Nestle
    if name == "Nestle":
        return 84.32, "CHF"
    else:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        if not data.empty:
            price = data['Close'].iloc[0]
            info = stock.info
            currency = info.get('currency', 'USD')  # Default to USD if currency is not found
            return price, currency
        else:
            raise ValueError(f"Could not fetch data for {ticker}")

# Function to get exchange rate
def get_exchange_rate(currency):
    c = CurrencyRates()
    try:
        rate = c.get_rate(currency, 'GBP')
        return rate
    except Exception as e:
        print(f"Error fetching exchange rate for {currency}: {e}. Defaulting to 1.0.")
        return 1.0  # Default to 1 if there's an issue with the API

# Initialize list for storing results
results = []

# Fetch stock price and currency, and calculate value in GBP
for stock in data:
    try:
        price, currency = get_stock_price(stock['ticker'], stock['name'])
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
    except Exception as e:
        print(f"Error processing {stock['name']} ({stock['ticker']}): {e}")
        continue

# Convert to DataFrame
df = pd.DataFrame(results)

# Write to CSV
df.to_csv("stock_prices.csv", index=False)

print("Stock prices saved to 'stock_prices.csv'")