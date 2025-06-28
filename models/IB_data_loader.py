import os
import sys
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from ib_insync import IB, Stock, util
#import shutil
import pandas as pd

class HistoricalDataWorker(QThread):

    # Signal emitted when data is ready to be sent to the UI
    data_ready = pyqtSignal(list)
    # Signal emitted when an error occurs
    error_signal = pyqtSignal(str)
    # Signal emitted to update progress (e.g., progress bar)
    update_progress = pyqtSignal()

    # Constructor to initialize the worker thread with required parameters
    def __init__(self, df_asset_list, duration, end_date, frequency, logger, parent=None):
        super().__init__(parent)
        self.df_asset_list = df_asset_list  # List of assets to fetch data for
        self.duration = duration            # Duration string (e.g., '1 M', '2 D')
        self.end_date = end_date            # End date/time for historical data
        self.frequency = frequency          # Frequency of data (e.g., 'day', 'min')
        self.logger = logger                # Logger object for logging messages

    # This method runs in a separate thread and launches the asyncio event loop
    def run(self):
        asyncio.run(self.fetch_data(self.duration, self.end_date, self.frequency, self.logger))

    # Coroutine that connects to IB and fetches historical data
    async def fetch_data(self, duration, end_date, frequency, logger):

        ib = IB()  # Create an instance of IB API client

        try:
            # Connect asynchronously to IB Gateway or TWS
            await ib.connectAsync('127.0.0.1', 4001, clientId=1)

            counter = 0  # Counter to track processed assets

            # Iterate over the assets
            for row_asset in self.df_asset_list.itertuples():

                symbol = row_asset.symbol       # Extract symbol from row
                #exchange = row_asset.exchange 
                self.logger.printAndLogger(f" {symbol}")

                # Define the contract for the asset
                contract = Stock(symbol, 'SMART', 'USD')

                # List to store the fetched bar data as DataFrames
                all_bars = []

                # Request historical bar data for the asset
                bars = await ib.reqHistoricalDataAsync(
                    contract,
                    endDateTime=end_date,
                    durationStr=duration,
                    barSizeSetting=f'1 {frequency.lower()}',
                    whatToShow='TRADES',
                    useRTH=False,       # Set to True to use only regular trading hours
                    formatDate=2        # Use yyyyMMdd HH:mm:ss format
                )

                # Convert fetched bars to a list of tuples (for optional UI transmission)
                data = [(bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume) for bar in bars]

                if bars:
                    logger.printAndLogger("control 1 - bars")

                    # Convert bars to DataFrame using ib_insync's utility function
                    df = util.df(bars)
                    all_bars.append(df)

                    # Concatenate all dataframes if any
                    if len(all_bars) > 0:
                        df_new_data = pd.concat(all_bars, ignore_index=True)

                        # Convert date column to datetime with UTC
                        df_new_data['date'] = pd.to_datetime(df_new_data['date'], utc=True)
                        logger.printAndLogger(f"    Records read from broker: {len(df_new_data)}")

                # If new data was fetched, continue with file merging and saving
                if len(df_new_data) > 0:

                    # Build output file path
                    csv_directory = "data/financial_data/"
                    #file_name = f"{csv_directory}IB_{frequency}/{frequency}_{exchange}_{symbol}_.csv"
                    file_name = f"{csv_directory}IB_{frequency}/{frequency}_{symbol}_.csv"
                    logger.printAndLogger(f"file_name: {file_name}")

                    # If file already exists, merge with existing data
                    if os.path.exists(file_name):

                        # Read existing data from CSV file
                        df_existing = pd.read_csv(file_name)
                        logger.printAndLogger(f"    Records read from file: {len(df_existing)}")

                        # Convert date column to datetime with UTC
                        df_existing['date'] = pd.to_datetime(df_existing['date'], utc=True)

                        # Merge existing and new data, removing duplicates by 'date'
                        if len(df_new_data) > 0:
                            df_combined = pd.concat([df_existing, df_new_data], ignore_index=True)
                            logger.printAndLogger(f"     Combined records: {len(df_combined)}")

                            df_combined = df_combined.drop_duplicates(subset=['date'])
                            logger.printAndLogger(f"     Records after removing duplicates: {len(df_combined)}")

                            df_new_data = df_combined.copy()
                        else:
                            df_new_data = df_existing

                    # Sort final data by date and save to CSV
                    df_new_data['date'] = pd.to_datetime(df_new_data['date'], utc=True)
                    df_new_data = df_new_data.sort_values(by='date')

                    # Extract path directory
                    directory = os.path.dirname(file_name)

                    # Create directory if not exists
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True)
                        
                    df_new_data.to_csv(file_name, index=False)
                    print(f"    Concatenated data for {symbol} updated and saved to {file_name}")

                else:
                    logger.printAndLogger("0 records retrieved")

                # Update UI or progress indicator
                counter += 1
                self.update_progress.emit()

        except Exception as e:
            print(e)
            self.error_signal.emit(str(e))  # Emit error message to UI

        finally:
            print("disconnected IB")
            ib.disconnect()  # Ensure IB is disconnected
