import os  # For file path handling
import pandas as pd  # For DataFrame operations
from datetime import datetime  # To handle date/time
import logging  # For logging actions
import shutil  # For file copying
from libraries.Lib_Alpaca import Alpaca  # Custom library for Alpaca broker
import yfinance as yf
import time
import gc  # For garbage collection
import requests # For HTTP requests (if needed, not used in the provided code)
import re

# AssetManager class to manage asset data
# This class handles fetching, saving, and loading asset data from Alpaca and CSV files.
class AssetManager:

    def __init__(self, dir_asset="", dir_config=""):
        self._DEBUG = False  # Debug flag
        self._now = datetime.now()  # Current timestamp
        # Default directory for asset files
        self._dir_asset_file = dir_asset if dir_asset else "data\\Assets\\"
        # Default directory for config files
        self._dir_config_file = dir_config if dir_config else "data\\Config\\"
        # Log file path based on current date
        self._log_filename = f'LOG\\Assets_{self._now.strftime("%Y%m%d")}.log'

        # Set up logging configuration
        logging.basicConfig(
            format='[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s',
            filename=self._log_filename,
            level=logging.DEBUG if self._DEBUG else logging.INFO
        )
        self._logger = logging.getLogger("jsonSocket")  # Logger instance

    @property
    def DEBUG(self):
        return self._DEBUG

    @DEBUG.setter
    def DEBUG(self, value):
        self._DEBUG = value

    @property
    def dir_asset_file(self):
        return self._dir_asset_file

    @dir_asset_file.setter
    def dir_asset_file(self, value):
        self._dir_asset_file = value

    @property
    def dir_config_file(self):
        return self._dir_config_file

    @dir_config_file.setter
    def dir_config_file(self, value):
        self._dir_config_file = value

    @property
    def logger(self):
        return self._logger

    def save_assets_to_csv(self):
        print("INICIO save_assets_to_csv    ")
        # Start logging the process
        self._logger.info("Starting to fetch active assets from Alpaca and save to CSV.")

        alpaca_broker = Alpaca()  # Initialize Alpaca broker

        try:
            # Fetch active assets
            active_assets = alpaca_broker.get_assets(status='active', asset_class='us_equity')
            self._logger.info(f"Getting {len(active_assets)} active assets from Alpaca.")
        except Exception as e:
            # Log any errors during fetch
            self._logger.error(f"Error getting active assets from Alpaca: {e}")
            return False, None

        df = pd.DataFrame(active_assets)  # Convert list to DataFrame

        if not df.empty:
            # Remove slash from symbol names
            df['symbolR'] = df['symbol'].str.replace("/", "", regex=False)
            # Ensure columns exist or initialize
            if 'min_order_size' not in df.columns:
                df['min_order_size'] = 0
            if 'min_trade_increment' not in df.columns:
                df['min_trade_increment'] = 0
            if 'price_increment' not in df.columns:
                df['price_increment'] = 0

        # Sort by symbol
        df = df.sort_values(by='symbol', ascending=True)
        file_name = os.path.join(self.dir_asset_file, "Assets.csv")  # Path to save CSV

        if os.path.exists(file_name):
            # Create a backup copy if file exists
            current_date_str = datetime.now().strftime("%Y_%m_%d")
            backup_file = file_name.replace(".csv", f"_{current_date_str}.csv")
            shutil.copy(file_name, backup_file)

        try:
            # Save DataFrame to CSV
            df.to_csv(file_name, index=False, encoding='utf-8')
            self._logger.info(f"Save file {file_name} successfully.")
        except Exception as e:
            # Log any errors while saving
            self._logger.error(f"Error saving CSV file: {e}")
            return False, None

        return True, df  # Return success flag and DataFrame

    def load_assets_from_csv(self):
        
        file_name = os.path.join(self.dir_asset_file, "Assets.csv")  # Path to load CSV

        if os.path.exists(file_name):
            # Load CSV into DataFrame and return
            return pd.read_csv(file_name, index_col=0, header=0, encoding='utf-8')
        return None  # Return None if file doesn't exist

    # Function to detect the type of asset
    """def detect_asset_type(self, df, symbol_column):

        types = []
        for symbol in df[symbol_column]:
            print(f"symbol: {symbol}")
            try:
                info = yf.symbol(symbol).info                
                type = info.get('quoteType', 'unknown')
            except Exception as e:
                print(f"Error al obtener info para {symbol}: {e}")
                type = 'unknown'        
            types.append(type)
            time.sleep(0.5)  # to avoid being blocked by Yahoo
        
        # Add asset type
        df['asset_type'] = types
        
        # Create name new file
        file_name = os.path.join(self.dir_asset_file, "Assets_with_type.csv")  # Path to save CSV

        # Save new file with asset type
        #df.to_csv(file_name, index=False, encoding='utf-8')

        return df"""


    """def classify_asset_type(self, df):

        refined_types = []
        types = []
        
        for row in  df.itertuples():

            symbol = getattr(row, 'symbol')
            name = getattr(row, 'name').lower()
            quote_type = 'unknown'
            
            print(f"    symbol: {symbol}")
            print(f"    Alpaca name: {name}")

            # Opción 1: "unit" rodeada por espacios o al inicio/final de texto
            patron_unit = r'(^|\s)unit(\s|$)'
            patron_fund = r'(^|\s)fund(\s|$)'
            patron_reit = r'(^|\s)reit(\s|$)'

            # Refined classification based on keywords
            if 'etf' in name or 'valuefund' in name:
                asset_type = 'ETF'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'ETF'
            elif ('common stock' in name
                or 'voting' in name):
                asset_type = 'Stock'    
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'warrant' in name:
                asset_type = 'Warrant'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'right' in name:
                asset_type = 'Right'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif re.search(patron_unit, name, re.IGNORECASE):
                asset_type = 'Unit'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif re.search(patron_reit, name, re.IGNORECASE):
                asset_type = 'REIT'     # Real Estate Investment Trust
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif ('preferred' in name
                or '.PR' in symbol.upper()):
                asset_type = 'Preferred stock'      # Special Purpose Acquisition Company
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif ('adr' in name
                or 'sponsored' in name
                or 'depositary' in name
                or 'depository' in name
                ):                    
                asset_type = 'ADR'      # American Depositary Receipt
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'acquisition' in name:                
                asset_type = 'SPAC'      # Special Purpose Acquisition Company
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'subordinated debentures' in name:                
                asset_type = 'bond'
                if quote_type == 'unknown': quote_type = 'bond'
            elif quote_type == 'equity':
                asset_type = 'Stock'
            elif symbol.upper().endswith('.A'):
                asset_type = 'Stock'    
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'ordinary share' in name:
                print(f"    Ordinary share: {name}")
                asset_type = 'Stock'    
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif re.search(patron_fund, name, re.IGNORECASE):
                asset_type = 'fund'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'FUND'
            else:
                asset_type = 'Stock 1'

            refined_types.append(asset_type)
            types.append(quote_type)
            #time.sleep(0.5)  # Prevent rate-limiting by Yahoo

        df['asset_type'] = types
        df['refined_asset_type'] = refined_types
        
        # Create name new file
        file_name = os.path.join(self.dir_asset_file, "Assets_with_type.csv")  # Path to save CSV

        # Save new file with asset type
        df.to_csv(file_name, index=False, encoding='utf-8')

        return df"""



    def classify_asset_type(self, df):

        refined_types = []
        types = []
        
        for row in  df.itertuples():

            symbol = getattr(row, 'symbol')
            name = getattr(row, 'name').lower()
            print(f"symbol: {symbol}")
            asset_type = 'unknown'
            quote_type = 'unknown'
            long_name = ''
            short_name = ''

            try:
                #url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=quoteType"
                #response = requests.get(url)
                #data = response.json()
                #quote_type = data['quoteSummary']['result'][0]['quoteType'].lower() if 'result' in data['quoteSummary'] and len(data['quoteSummary']['result']) > 0 else 'unknown'
                #long_name = data['quoteSummary']['result'][0].get('longName', '').lower() if 'result' in data['quoteSummary'] and len(data['quoteSummary']['result']) > 0 else ''
                #short_name = data['quoteSummary']['result'][0].get('shortName', '').lower() if 'result' in data['quoteSummary'] and len(data['quoteSummary']['result']) > 0 else ''

                
                """ticker = yf.Ticker(symbol)
                summary = ticker.get_info()  # mismo que .info pero menos problemático
                quote_type = summary.get("quoteType") or "unknown"
                long_name = summary.get("longName") or ''
                short_name = summary.get("shortName") or ''"""

                ticker = yf.Ticker(symbol)
                info = ticker.info
                quote_type = info.get('quoteType', '').lower()
                long_name = info.get('longName', '').lower()
                short_name = info.get('shortName', '').lower()

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                asset_type = 'unknown'
                quote_type = 'unknown'
                long_name = ''
                short_name = ''
            finally:
                gc.collect()  # Forzar limpieza
                info = None  # Clear info to free memory

            print(f"    quote_type: {quote_type}")
            print(f"    long_name: {long_name}")
            print(f"    short_name: {short_name}")
            print(f"    asset_type: {asset_type}")
            print(f"    Alpaca name: {name}")
            
            # Refined classification based on keywords
            if 'etf' in quote_type or 'etf' in long_name or 'etf' in short_name or 'etf' in name:
                asset_type = 'ETF'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'ETF'
            elif ('common stock' in long_name or 'common stock' in short_name or 'common stock' in name
                or 'voting' in long_name or 'voting' in short_name or 'voting' in name):
                asset_type = 'Stock'    
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'warrant' in long_name or 'warrant' in short_name or 'warrant' in name:
                asset_type = 'Warrant'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'right' in long_name or 'right' in short_name or 'right' in name:
                asset_type = 'Right'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'unit' in long_name or 'unit' in short_name or 'unit' in name:
                asset_type = 'Unit'
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'reit' in long_name or 'reit' in short_name or 'reit' in name:
                asset_type = 'REIT'     # Real Estate Investment Trust
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif ('preferred' in long_name or 'preferred' in short_name or 'preferred' in name
                or '.PR' in symbol.upper()):
                asset_type = 'Preferred stock'      # Special Purpose Acquisition Company
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif ('adr' in long_name or 'adr' in short_name or 'adr' in name
                or 'sponsored' in long_name or 'sponsored' in short_name or 'sponsored' in name
                or 'depositary' in long_name or 'depositary' in short_name or 'depositary' in name
                or 'depository' in long_name or 'depository' in short_name or 'depository' in name
                ):                    
                asset_type = 'ADR'      # American Depositary Receipt
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'acquisition' in long_name or 'acquisition' in short_name or 'acquisition' in name:                
                asset_type = 'SPAC'      # Special Purpose Acquisition Company
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            elif 'subordinated debentures' in long_name or 'subordinated debentures' in short_name or 'subordinated debentures' in name:                
                asset_type = 'bond'
                if quote_type == 'unknown': quote_type = 'bond'
            elif quote_type == 'equity':
                asset_type = 'Stock'
            elif quote_type != '':
                asset_type = quote_type.capitalize()
            elif symbol.upper().endswith('.A'):
                asset_type = 'Stock'    
                if quote_type == 'unknown' or quote_type == '': quote_type = 'EQUITY'
            else:
                asset_type = 'Stock 1'
                


            refined_types.append(asset_type)
            types.append(quote_type)
            time.sleep(0.5)  # Prevent rate-limiting by Yahoo

        df['asset_type'] = types
        df['refined_asset_type'] = refined_types
        
        # Create name new file
        file_name = os.path.join(self.dir_asset_file, "Assets_with_type.csv")  # Path to save CSV

        # Save new file with asset type
        df.to_csv(file_name, index=False, encoding='utf-8')

        return df
