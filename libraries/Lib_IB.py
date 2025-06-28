from ib_insync import *
import pandas as pd
import datetime

# InteractiveBrokersClient class to manage connections and data retrieval from Interactive Brokers
class InteractiveBrokersClient:

    # Initialize the Interactive Brokers client with connection parameters
    def __init__(self, host='127.0.0.1', port=4001, client_id=10):

        # Initialize the IB client with connection parameters
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()  # Create an IB object for managing the connection

    # Connect to Interactive Brokers TWS or IB Gateway
    def connect(self):

        # Connect to Interactive Brokers TWS or IB Gateway
        self.ib.connect(self.host, self.port, self.client_id)
        print(f"Connected to Interactive Brokers at {self.host}:{self.port} with clientId {self.client_id}")

    # Disconnect from Interactive Brokers TWS or IB Gateway
    def disconnect(self):

        # Disconnect from Interactive Brokers
        self.ib.disconnect()
        print("Disconnected from Interactive Brokers")

    # Check if the client is connected and market data is set to live
    def isConnected(self):

        # Check if the client is connected and market data is set to live
        if self.ib.isConnected() and self.ib.reqMarketDataType(1):  # Market data type 1 = live
            return True
        return False

    # Get historical data for a single symbol
    def get_historical_data(self, symbol, exchange='SMART', currency='USD', duration='1 D', bar_size='1 min', what_to_show='TRADES', use_rth=True, tipo="STOCK"):

        # Download historical data for a single symbol
        stock = Stock(symbol, exchange, currency)  # Define contract
        bars = self.ib.reqHistoricalData(
            stock,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=use_rth,
            formatDate=1
        )
        df = util.df(bars)  # Convert bars to DataFrame
        return df

    # Show the DataFrame in console
    def show_data(self, df):

        # Print the DataFrame to console
        print(df)

    # Get historical data for a ticker over a range of business days
    def get_historical_data_by_days(self, ticker, filename="", frec='Min', diaIni=0, diaFin=1, diaInc=1, isCrypto=False, horarioRegulado=False):
        
        """
        Downloads historical bar data for a ticker over a range of business days.

        :param ticker: Symbol to download (e.g., 'AAPL')
        :param filename: CSV output file (optional)
        :param frec: Frequency of bars ('Min' for minute, 'Hor' for hourly)
        :param diaIni: Starting offset in days (from today)
        :param diaFin: Ending offset in days
        :param diaInc: Day increment for each request
        :param isCrypto: If true, request crypto data
        :param horarioRegulado: If true, only request regular trading hours
        """
        what_to_show = "TRADES"

        # Define contract depending on asset type
        if isCrypto:
            contract = Crypto(ticker, 'PAXOS', 'USD')
            what_to_show = "AGGTRADES"
        else:
            contract = Stock(ticker, 'SMART', 'USD')

        all_data = pd.DataFrame()  # Initialize empty DataFrame to accumulate data
        end_date = datetime.datetime.now()  # Set the initial end date to now

        barSizeSetting = '1 min'  # Default to 1-minute bars
        if frec == 'Hor':
            barSizeSetting = '1 hour'  # Change to 1-hour bars if requested

        cont = 0  # Counter for iterations
        durStr = f"{diaInc} D"  # Duration string for request

        for _ in range(diaIni, diaFin, diaInc):
            cont += 1

            # Request historical data from IB
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=end_date,
                durationStr=durStr,
                barSizeSetting=barSizeSetting,
                whatToShow=what_to_show,
                useRTH=horarioRegulado,
                formatDate=1,
            )

            df = util.df(bars)  # Convert to DataFrame

            # Optional timezone conversion to Europe/Madrid
            # df['date'] = pd.to_datetime(df['date'])
            # df['date'] = df['date'].dt.tz_convert('Europe/Madrid')

            if df is not None and not df.empty:
                all_data = pd.concat([df, all_data], ignore_index=True)  # Append to main DataFrame
                end_date = df['date'].min() - pd.Timedelta(hours=1)  # Update end date for next request
            else:
                print("df empty")
                end_date -= pd.Timedelta(days=diaInc)  # Manually adjust end date if data is missing

        return all_data  # Return the final DataFrame

        # Save to CSV if desired
        # all_data.to_csv(filename, index=False)

        # Print confirmation
        # print(f"Data saved to {filename}")
