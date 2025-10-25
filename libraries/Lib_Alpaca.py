import os
import requests  
import pandas as pd
import json
import pytz  # For timezone handling

# Import necessary libraries
class Alpaca:

    # Initialization of the Alpaca class
    def __init__(self, environment="test", alpaca_account_name="Paper"):
        
        print(f"Environment: {environment}")
        print(f"Alpaca account name: {alpaca_account_name}")

        # Check for personal config file
        if os.path.exists("config/personal_Lib_Alpaca.json"):
            with open("config/personal_Lib_Alpaca.json", 'r') as file:
                config = json.load(file)
        else:
            with open("config/Lib_Alpaca.json", 'r') as file:
                config = json.load(file)
        
        if environment.lower() == "real":
            # Assign live credentials
            API_KEY = config['Live']['API_KEY']
            API_SECRET = config['Live']['API_SECRET']
            BASE_URL = config['Live']['BASE_URL']
        elif environment.lower() == "test":
            # Assign test credentials
            API_KEY = config[alpaca_account_name]['API_KEY']
            API_SECRET = config[alpaca_account_name]['API_SECRET']
            BASE_URL = config[alpaca_account_name]['BASE_URL']

        print(f"API_KEY: {API_KEY}")
        print(f"API_SECRET: {API_SECRET}")
        print(f"BASE_URL: {BASE_URL}")

        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret,
            'Content-Type': 'application/json'
        }

        # U.S. Eastern timezone for market time alignment
        self.et = pytz.timezone("US/Eastern")
        print(f"Eastern timezone object: {self.et}")

    # Function to get the list of available assets
    def get_assets(self, status=None, asset_class=None, exchange=None):
        """
        Fetches the list of assets from Alpaca API.

        Args:
            status (str): Filter by asset status ('active', 'inactive', or 'all').
            asset_class (str): Filter by asset class ('us_equity', 'crypto').
            exchange (str): Filter by exchange (e.g., 'NASDAQ', 'NYSE').

        Returns:
            list: List of asset dictionaries or raises an error if the request fails.
        """
        url = f"{self.base_url}/v2/assets"
        params = {}

        if status:
            params["status"] = status
        if asset_class:
            params["asset_class"] = asset_class
        if exchange:
            params["exchange"] = exchange

        # Make the GET request to the Alpaca API
        response = requests.get(url, headers=self.headers, params=params)

        # Check response status
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
