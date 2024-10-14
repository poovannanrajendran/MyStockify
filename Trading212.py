import requests
import json
import pandas as pd
from settings import API_KEY  # Import API key from settings.py

# Trading212 API URL
url = "https://live.trading212.com/api/v0/equity/portfolio"

# Use the API key from settings.py
headers = {
    "Authorization": API_KEY
}

# Fetch data from Trading212 API
response = requests.get(url, headers=headers)

# Check if request is successful
if response.status_code == 200:
    # Load the response data into a Python list
    data = response.json()

    # Write the raw data to a JSON file (formatted)
    with open("portfolio_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    # Format the data into a pandas DataFrame
    formatted_data = []
    for item in data:
        formatted_data.append({
            "Ticker": item['ticker'],
            "Quantity": item['quantity'],
            "Average Price": item['averagePrice'],
            "Current Price": item['currentPrice'],
            "Profit/Loss": item['ppl'],
            "FX Profit/Loss": item['fxPpl'],
            "Initial Fill Date": item['initialFillDate'],
            "Frontend": item['frontend'],
            "Max Buy": item['maxBuy'],
            "Max Sell": item['maxSell'],
            "Pie Quantity": item['pieQuantity']
        })

    # Create a pandas DataFrame
    df = pd.DataFrame(formatted_data)

    # Write the DataFrame to a CSV file
    df.to_csv("portfolio_data.csv", index=False)

    print("Data written to portfolio_data.json and portfolio_data.csv")

else:
    print(f"Failed to fetch data: {response.status_code}")
