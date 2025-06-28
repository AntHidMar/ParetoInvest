import os  # For file path handling
import pandas as pd  # For DataFrame operations
from datetime import datetime  # To handle date/time
import logging  # For logging actions
import shutil  # For file copying
from libraries.Lib_Alpaca import Alpaca  # Custom library for Alpaca broker

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
