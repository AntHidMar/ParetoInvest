import math
import random
import re
import os
import numpy as np
import pandas as pd
from functools import reduce
#from jmetal.core.problem import FloatProblem
#from jmetal.core.solution import FloatSolution
import timeit
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import warnings
warnings.filterwarnings("ignore")



import os
from datetime import datetime, timedelta

class GenerateStatisticalFilesJMetal:
    # Class to generate statistical files for JMetal optimization framework.
    def __init__(self, population_size, num_est, num_tot, directory, start_date, end_date,
                 class_assets, exchange, increase_freq, increase, window_freq,
                 window, frequency, df_assets):

        # Store initialization parameters
        self.population_size = population_size
        self.num_est = num_est                      # Number of assets to invest in
        self.num_tot = num_tot                      # Total number of assets to consider
        self.directory = directory
        self.start_date = start_date
        self.end_date = end_date
        self.class_assets = class_assets
        self.exchange = exchange
        self.increase_freq = increase_freq
        self.increase = increase                    # Step size for moving window
        self.window_freq = window_freq
        self.window = window
        self.frequency = frequency
        self.df_assets = df_assets
        self.number_of_assets = num_est

        # Generate filenames for each asset based on its symbol and frequency
        df_assets['File_Name'] = df_assets['symbol'].astype(str).apply(
            lambda x: f"{frequency}_{x}_.csv")

        # Obtain full paths for all files using the generated filenames
        files = list(self.obtain_file_paths(df_assets, 'File_Name', self.directory).values())

        # Sort files by file size in descending order and select top 'num_tot'
        files = sorted(files, key=lambda x: os.stat(x).st_size, reverse=True)
        files = files[:num_tot]

        # Error check: Ensure enough files are available
        if len(files) < num_tot:
            print("ERROR 1. The number of available files/companies must not be less than the total desired.")
            print(f"len(files): {len(files)}")
            print(f"numTot: {num_tot}")
            return

        # Error check: Ensure total number of companies is not less than number to invest in
        elif num_tot < num_est:
            print("ERROR 2. The total number of companies to analyze must not be less than the number to invest in.")
            return

        # Define file subsets for total and studied assets
        files_total = files[:num_tot]      # Complete set
        files_studied = files[:num_est]    # Subset to analyze

        # Determine actual end date (use yesterday if none provided)
        start = start_date
        if end_date is None:
            end = datetime.now() - timedelta(days=1)
        else:
            end = end_date

        # Generate date intervals for analysis
        cont = increase
        date_list = [start]
        start_tmp = start
        end_tmp = self._get_next_date(increase_freq, start, cont)
        print(f"start: {start}  --  end: {end}  --  endTmp: {end_tmp}")
        # Loop through date ranges until reaching end date
        while end_tmp <= end:
            print(f"startTmp: {start_tmp}  --  endTmp: {end_tmp}")

            # Format dates as strings for file naming and reading
            start_str = start_tmp.strftime('%Y-%m-%d')
            end_str = end_tmp.strftime('%Y-%m-%d')

            # Read historical data from files within date range
            matrix_pct, mean_returns, total_assets = self.__read_from_file(
                files, start_str, end_str, num_tot)

            # Sort assets by mean returns in descending order
            mean_returns = mean_returns.sort_values(ascending=False)
            matrix_pct = matrix_pct[mean_returns.index]

            print(len(matrix_pct), len(mean_returns), total_assets)

            # Error check: Ensure enough assets are available
            if total_assets < num_est:
                return "ERROR 3. Total number of assets must not be less than number of assets to invest in."

            # Store historical returns matrix and covariance matrix
            self.hist_stock_returns = matrix_pct
            self.cov_hist_return = matrix_pct.cov()

            # Create directory to save statistical files
            dir_csv = f"resources/JMetal_Files/{exchange}_{num_est}_{num_tot}"
            os.makedirs(dir_csv, exist_ok=True)

            # Save covariance matrix to CSV
            self.cov_hist_return.to_csv(
                f"{dir_csv}/_cov_hist_return_{exchange}_{num_est}_{num_tot}_{start_tmp.strftime('%Y%m%d')}_{end_tmp.strftime('%Y%m%d')}_.csv")

            # Save mean returns to CSV
            mean_returns.to_csv(
                f"{dir_csv}/_mean_hist_return_{exchange}_{num_est}_{num_tot}_{start_tmp.strftime('%Y%m%d')}_{end_tmp.strftime('%Y%m%d')}_.csv")

            # Store the mean returns for further use
            self.mean_hist_return = mean_returns

            # Move to the next date interval
            date_list.append(end_tmp)
            cont += increase
            start_tmp = end_tmp
            end_tmp = self._get_next_date(increase_freq, start, cont)

    # Function to obtain file paths from a DataFrame column.
    def obtain_file_paths(self, df, col_name, directory):
        # Create dictionary mapping file names to full paths
        return {row[col_name]: os.path.join(directory, row[col_name]) for _, row in df.iterrows()}
   
    # Returns a list of file paths that match the given prefix.
    def listfilesWithPath(self, path, prefijo):         
        
        # Esta forma se bloquea cuando hay muchos archivos.
        #return [obj.name for obj in scandir(path) if obj.is_file() and obj.name.startswith(prefijo) ]
        #return [path+obj.name for obj in sorted(scandir(path), key=os.path.getmtime) if obj.is_file() and obj.name.startswith(prefijo) ]
        #return [path+obj.name for obj in scandir(path) if obj.is_file() and obj.name.startswith(prefijo) ]

        # Forma más eficiente de devolver archivos.
        files = []
        for dirpath, subdirs, files in os.walk(path):
            files.extend(os.path.join(dirpath, x) for x in files if x.startswith(prefijo))
        return files

    # Function to obtain file paths based on names in a DataFrame column.
    def get_files_paths(df, name, folder):
        """
        Search for files in the specified folder based on names in a DataFrame column.

        :param df:      DataFrame containing the file names
        :param name:    Name of the column in the DataFrame that contains the file names
        :param folder:  Folder path where to search for the files
        :return:        Dictionary mapping {File_Name: full_path} for files that exist
        """
        rutas = {}
        for File_Name in df[name].dropna().unique():  # Remove NaN values and duplicated entries
            full_path = os.path.join(folder, File_Name)  # Construct full path
            if os.path.isfile(full_path):  # Check if the file exists at that path
                rutas[File_Name] = full_path  # Add it to the dictionary
        return rutas

    # Function to calculate the next date based on the frequency and increment.
    def _get_next_date(self, increaseFreq, start, cont):
        """
        Calculate a new date by increasing the given start date by a certain amount of time.

        :param increaseFreq: Frequency to increase ("year", "month", "week", or "day")
        :param start:        Starting datetime object
        :param cont:         Number of units to add
        :return:             New datetime object with the increment applied
        """
        endTmp = None

        if increaseFreq == "year":
            endTmp = start + relativedelta(years=cont)
        elif increaseFreq == "month":
            endTmp = start + relativedelta(months=cont)
        elif increaseFreq == "week":
            endTmp = start + timedelta(weeks=cont)
        elif increaseFreq == "day":
            endTmp = start + timedelta(days=cont)

        return endTmp

    # Function that reads the data to be studied and loads it into dataframes.
    # It returns:
    # - A dataframe with daily log returns of each asset (merged across all files).
    # - A dataframe with total returns of each asset.
    # - The number of files processed.
    def __read_from_file(self, filesname: [str], startDate, endDate, numTot):
        
        if filesname is None:
            raise FileNotFoundError("filesname can not be None")

        df = pd.DataFrame()      # To store log returns for all assets.
        dfR = pd.DataFrame()     # To store total return per asset.
        retornos = []            # List to hold total return of each asset.
        cols = []                # List of asset names (column names).
        cont = 1                 # Counter to control number of files processed.

        for file in filesname:
            print(f"cont:{cont} - file:{file}")

            if cont > numTot:
                break

            # Read the CSV file, parse the first column as datetime (removing timezone info if present)
            dfTemp = pd.read_csv(file, header=0, encoding='utf-8', 
                                parse_dates=[0], index_col=[0], 
                                date_parser=lambda x: pd.to_datetime(x.rpartition('+')[0]))

            dfTemp.index = pd.to_datetime(dfTemp.index)  # Ensure datetime index
            dfTemp = dfTemp.loc[startDate:endDate]       # Filter by date range
            print("len(dfTemp)", len(dfTemp))

            # Remove duplicate timestamps, keeping only the first occurrence
            dfTemp = dfTemp[~dfTemp.index.duplicated(keep='first')]

            if len(dfTemp) > 0:
                dfTemp = dfTemp.sort_index()             # Ensure data is sorted chronologically
                dfTemp = dfTemp.resample('d').last()     # Resample to daily frequency using last available value

                # Extract the company name from the file name
                newName = file.replace('_.csv','')\
                                .replace('C:\\Datos\\EspacioTrabajoAnaconda\\SII\\Test\\Datos\\Historico\\alpaca_Dia\\renombrar\\','')\
                                .replace('alpaca_Dia_','')

                print(newName)
                cols.append(newName)                     # Store asset name

                # Rename 'close' column to asset name
                dfTemp.rename(columns={ 'close': newName }, inplace=True)
                dfTemp = dfTemp[[newName]]               # Keep only the renamed column

                # Convert data to numeric, log returns, clean NaNs and infinite values
                dfTemp[newName] = dfTemp[newName].apply(pd.to_numeric, errors='coerce')
                dfTemp[newName] = dfTemp.pct_change().apply(lambda x: np.log(1 + x))
                dfTemp[newName].replace([np.inf, -np.inf], np.nan, inplace=True)
                dfTemp[newName].dropna(inplace=True)

                retornos.append(dfTemp[newName].sum())   # Calculate total log return for the asset

                # Merge the asset's return data with the global dataframe
                if len(df) > 0:
                    df = pd.concat([dfTemp, df], axis=1)
                else:
                    df = dfTemp
            else:
                print("   No data exists for the asset analyzed.")

            cont += 1

        # Fill any missing values in the merged dataframe using forward and backward fill
        df = df.fillna(method="ffill")
        df = df.fillna(method="bfill")
        df = df.sort_index()

        # Store the total returns for each asset in a single-row DataFrame
        dfR.loc[0, cols] = retornos
        dfR = dfR.sum()  # Optionally aggregate to a single series

        return df, dfR, len(filesname)

    # Function that reads the data to be studied and loads it into dataframes.
    """def __read_from_file(self, filesname: [str], startDate, endDate, numTot):
        
        if filesname is None:
            raise FileNotFoundError("filesname can not be None")

        df=pd.DataFrame()
        dfR=pd.DataFrame()
        retornos = []
        cols = []
        cont = 1
        for file in filesname:
            print(f"cont:{cont} - file:{file}")

            if cont > numTot:
                break 
            # Leemos datos
            dfTemp = pd.read_csv(file, header=0, encoding='utf-8', parse_dates=[0], index_col=[0], date_parser=lambda x: pd.to_datetime(x.rpartition('+')[0]))                
            dfTemp.index = pd.to_datetime(dfTemp.index)     # Convert to indexdatetime  
            
            dfTemp = dfTemp.loc[startDate:endDate]          # Selected date to study.
            print("len(dfTemp)", len(dfTemp))
            dfTemp = dfTemp[~dfTemp.index.duplicated(keep='first')]     # Delete duplicates, keeping the first one.

            if len(dfTemp) > 0:

                dfTemp = dfTemp.sort_index()
                dfTemp = dfTemp.resample('d').last()    # Resample to daily frequency
                # Get the company details from the data file.
                newName = file.replace('_.csv','').replace('C:\\Datos\\EspacioTrabajoAnaconda\\SII\\Test\\Datos\\Historico\\alpaca_Dia\\renombrar\\','').replace('alpaca_Dia_','')
                print(newName)
                cols.append(newName)    # Añadimos el nombre de la empresa a la lista de nombres de empresas.
                # Le damos a la columna close, para la empresa actual, el nombre de la empresa actual, así cuando estén todas 
                # las empresas concatenadas podamos identificar los datos de cada una de ellas.
                dfTemp.rename(columns={ 'close': newName }, inplace = True)
                dfTemp = dfTemp[[newName]]  # Seleccionamos solo la columna con el nombre de la empresa, eliminando el resto.
                dfTemp[newName] = dfTemp[newName].apply(pd.to_numeric, errors='coerce') # Convertimos datos a numérico.
                dfTemp[newName] = dfTemp.pct_change().apply(lambda x: np.log(1+x))      # Calculamos los datos en variaciones de porcentaje en logaritmo mas uno.           
                dfTemp[newName].replace([np.inf, -np.inf], np.nan, inplace=True)    # Evitamos infinitos.
                dfTemp[newName].dropna(inplace=True)   
                retornos.append(dfTemp[newName].sum())  # Sumamos todos las variaciones para calcular el retorno total.
                #print("retornos")
                #print(retornos)
                #print(sum(retornos))
                if len(df) > 0:                
                    #df = pd.merge(df, dfTemp, left_index=False, right_index=False)
                    df = pd.concat([dfTemp, df], axis=1)  # Concatenamos retornos.               
                else:
                    df = dfTemp
            else:
                print("   No existen datos para el activo analizado.")        
            
            cont+=1
            #print(df)
        
        df = df.fillna(method="ffill")  # Sustituimos valores nulos por valores posteriores.
        df = df.fillna(method="bfill")  # Sustituimos valores nulos por valores anteriores.
        df = df.sort_index()
        
        dfR.loc[0,cols] = retornos
        #dfR = dfR.mean()
        dfR = dfR.sum()

        
        return df, dfR, len(filesname)
    """
    # Function that reads asset data and calculates total return for each one.
    # The assets are sorted by their total return over a given time range.
    def __SortedByReturn(self, df_Assets, startDate, endDate, numTot):
        if df_Assets is None:
            raise FileNotFoundError("df_Assets cannot be None")

        retornos = []            # List to store individual asset returns
        cols = []                # Column names for the returns
        cont = 1                 # Counter for number of files processed
        arrayReturn = []         # Final output: list of dictionaries with return values

        for row in df_Assets.itertuples():

            print(f"cont:{cont} - {self.directory}")

            if cont > numTot:
                break

            # Construct full path to the file
            file = self.directory + "\\" + row.File_Name

            # Read CSV with date as index
            dfTemp = pd.read_csv(file, index_col=0, header=0, encoding='utf-8')
            dfTemp.index = pd.to_datetime(dfTemp.index)

            # Convert startDate and endDate to pandas timestamps
            startDate_ts = pd.Timestamp(startDate)
            endDate_ts = pd.Timestamp(endDate)

            # Get the time zone of the data (if any)
            tz_df = dfTemp.index.tz

            # Align start and end dates to the time zone of the data
            if startDate_ts.tzinfo is not None:
                startDate = startDate_ts.tz_convert(tz_df) if tz_df else startDate_ts
            else:
                startDate = startDate_ts.tz_localize(tz_df) if tz_df else startDate_ts

            if endDate_ts.tzinfo is not None:
                endDate = endDate_ts.tz_convert(tz_df) if tz_df else endDate_ts
            else:
                endDate = endDate_ts.tz_localize(tz_df) if tz_df else endDate_ts

            # Filter rows between start and end date
            dfTemp = dfTemp.loc[startDate:endDate]            
            dfTemp = dfTemp[~dfTemp.index.duplicated(keep='first')]

            if len(dfTemp) > 0:  
                dfTemp = dfTemp.sort_index()
                dfTemp = dfTemp.resample('d').last()  # Resample to daily frequency

                # Extract clean asset name from file name
                newName = row.File_Name.replace('Day_','').replace('_.csv','')
                cols.append(newName)
                dfTemp.rename(columns={ 'close': newName }, inplace=True)
                dfTemp = dfTemp[[newName]]

                # Convert column to numeric and compute log returns
                dfTemp[newName] = dfTemp[newName].apply(pd.to_numeric, errors='coerce')
                dfTemp[newName] = dfTemp.pct_change().apply(lambda x: np.log(1 + x))
                dfTemp[newName].replace([np.inf, -np.inf], np.nan, inplace=True)
                dfTemp[newName].dropna(inplace=True)

                # Compute cumulative return and store it
                retornos.append(dfTemp[newName].sum())
                arrayReturn.append({"Id": str(cont), "Return": sum(retornos)})
            
            else:    
                print("   No data available for the asset analyzed.")   

            cont += 1

        return arrayReturn

    """# Función que lee los datos a estudiar y los carga en dataframes.
    # def __SortedByReturn(self, filesname: [str], startDate, endDate, numTot):
    def __SortedByReturn(self, df_Assets, startDate, endDate, numTot):
        
        print(startDate, endDate, numTot)
        if df_Assets is None:
            raise FileNotFoundError("filesname can not be None")

        df=pd.DataFrame()
        dfR=pd.DataFrame()
        retornos = []
        cols = []
        cont = 1
        diccReturn = {}
        arrayReturn = []
        for row in df_Assets.itertuples():

            print(f"cont:{cont} - {self.directory}")
            #print(row)
            
            if cont > numTot:
                break
            #temp=pd.read_csv(file)  
            file = self.directory + "\\" + row.File_Name
            dfTemp=pd.read_csv(file, index_col=0, header=0, encoding='utf-8')
            
            #dfTemp = pd.read_csv(file, header=0, encoding='utf-8', parse_dates=[0], index_col=[0], date_parser=lambda x: pd.to_datetime(x.rpartition('+')[0]))                
            dfTemp.index = pd.to_datetime(dfTemp.index) 
            
            # Convertir startDate y endDate a Pandas Timestamp
            startDate_ts = pd.Timestamp(startDate)
            endDate_ts = pd.Timestamp(endDate)
            
            # Obtener la zona horaria del DataFrame (si tiene una)
            tz_df = dfTemp.index.tz  

            # Convertir startDate y endDate a la misma zona horaria
            # Si startDate_ts ya tiene una zona horaria (tz-aware), usa tz_convert
            if startDate_ts.tzinfo is not None:
                startDate = startDate_ts.tz_convert(tz_df) if tz_df else startDate_ts
            else:
                startDate = startDate_ts.tz_localize(tz_df) if tz_df else startDate_ts
            
            if endDate_ts.tzinfo is not None:
                endDate = endDate_ts.tz_convert(tz_df) if tz_df else endDate_ts
            else:
                endDate = endDate_ts.tz_localize(tz_df) if tz_df else endDate_ts
            
            dfTemp = dfTemp.loc[startDate:endDate]            
            dfTemp = dfTemp[~dfTemp.index.duplicated(keep='first')]
            
            #print(dfTemp)
            
            if len(dfTemp) > 0:  
                #print("++++")
                #print(len(dfTemp))
                dfTemp = dfTemp.sort_index()
                dfTemp = dfTemp.resample('d').last() #.dropna()

                #newName = file.replace('_.csv','').replace('C:\\Datos\\EspacioTrabajoAnaconda\\SII\\Test\\Datos\\Historico\\alpaca_Dia\\renombrados\\','').replace('alpaca_Dia_','')
                newName = row.File_Name.replace('Day_','').replace('_.csv','')
                cols.append(newName)
                dfTemp.rename(columns={ 'close': newName }, inplace = True)
                dfTemp = dfTemp[[newName]]
                
                dfTemp[newName] = dfTemp[newName].apply(pd.to_numeric, errors='coerce') # Convert data to numeric.                
                dfTemp[newName] = dfTemp.pct_change().apply(lambda x: np.log(1+x))      # Calculate returns in log scale                
                dfTemp[newName].replace([np.inf, -np.inf], np.nan, inplace=True)        # Avoid division by zero or log of zero.
                dfTemp[newName].dropna(inplace=True)                                    # Delete nulls.
                retornos.append(dfTemp[newName].sum())                                  # Sum all variations to calculate total return.

                arrayReturn.append({"Id":str(cont),"Return":sum(retornos)})             # Append the return to the array.
                
            else:    
                print("   Does not exist data for the asset analyzed.")   
            
            cont+=1
        
        return arrayReturn
    """
    # Function to calculate historical returns for specified months.
    def hist_return(self, stocks, months: [int]):
        '''
        Calculates stock returns for various months and returns a DataFrame.
        Input: List of months as integers.
        Output: Historical returns as a DataFrame.
        '''

        idx = []  # To store labels for each calculated return (e.g., '3_mon_return')
        df = pd.DataFrame()  # Initialize an empty DataFrame to store the returns

        for mon in months:
            # Calculate the return as the percentage difference between the first month and the given month.
            # Note: Assumes the first row (iloc[0]) corresponds to the most recent data.
            temp = (stocks.iloc[0, 1:] - stocks.iloc[mon, 1:]) / (stocks.iloc[mon, 1:])

            # Append the label for the current return period (e.g., '3_mon_return')
            idx.append(str(mon) + '_mon_return')

            # Convert the Series to a single-row DataFrame and concatenate it to the results
            df = pd.concat([df, temp.to_frame().T], ignore_index=True)

        # Assign the custom labels to the DataFrame index for clarity
        df.index = idx

        # Return the DataFrame containing historical returns for each specified month period
        return df
        
    """def hist_return(self, stocks, months: [int]):
        ''' It calculates Stock returns for various months and returns a dataframe.
            Input: Months in the form of a list.
            Output: Historical returns in the form of a DataFrame. '''
        idx=[]
        df=pd.DataFrame()
        for mon in months:
            # Diferencia entre el primer mes y cada uno de los meses indicados por el array de meses.
                # Dividimos entre el último mes para convertirlo en porcentajes.
            temp=(stocks.iloc[0,1:] - stocks.iloc[mon,1:])/(stocks.iloc[mon,1:])
            # Vamos añadiendo cada uno de los registros del indice
            # EJ: 3_mon_return, 6_mon_return, ...
            idx.append(str(mon)+'_mon_return')
            # Concatenamos cada uno de los cálculos.
            df=pd.concat([df, temp.to_frame().T], ignore_index=True)
        # Añadimos los índices generados para cada uno de los registros.
        df.index=idx
        
        # Devolveremos el retorno para cada uno de los meses indicados con respecto el primer mes.
        return df    """
