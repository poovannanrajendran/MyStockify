import requests
from settings import API_KEY  # Import API key from settings.py

# API Configuration
API_KEY = API_KEY
BASE_URL = "https://demo.trading212.com/api/v0/"
headers = {"Authorization": f"Bearer {API_KEY}"}

def fetch_account_info():
    response = requests.get(f"{BASE_URL}equity/account/info", headers=headers)
    
    # Check for errors in the response
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    try:
        return response.json()
    except requests.JSONDecodeError:
        print("Error: Response is not in JSON format.")
        print(response.text)  # Print the response text for further debugging
        return None

# Test fetching account info
account_info = fetch_account_info()
if account_info:
    print(account_info)
else:
    print("Failed to fetch account information.")
