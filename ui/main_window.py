from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QDateEdit, QPushButton, QWidget, QFrame, QProgressBar, QFileDialog,
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QDate
import models.Assets as Assets
import models.IB_data_loader as IB_data_loader
import models.GenerarArchivosEstadisticos_JMetal as genArch_JMetal
import models.JMetal_Worker as JMetalWorker
import libraries.Lib_Logger as lib_Logger
from datetime import datetime, date
import pandas as pd
import sys
import os
import glob




# MainWindow class for the ParetoInvest application
class MainWindow(QMainWindow):
    
    # Constructor for the MainWindow class
    def __init__(self, log):

        # Initialize the parent class
        super().__init__()
        
        # Initialize the logger
        self.assets_manager = Assets.AssetManager()
        
        # Logger
        self.log = log
        
        # Log the constructor call
        self.log.printAndLogger(" MainWindow constructor called")

        # Initial configuration
        self.setWindowTitle("ParetoInvest")
        self.setGeometry(100, 100, 800, 600)

        self.dir_data = "data\\Assets\\"
        self.df_Assets = None
        self.end_pydate = None

        # Set up the UI
        self.init_ui()

    # Definition UI components
    def init_ui(self):

        self.log.printAndLogger("Initializing UI components")

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create a panel (QFrame) for the top controls
        controls_panel = QFrame()
        controls_panel.setFrameShape(QFrame.StyledPanel)
        controls_layout = QHBoxLayout(controls_panel)

        # ---- Layouts inside the panel ----
        self.log.printAndLogger("Creating internal layouts")
        left_grid = QGridLayout()
        left_layout = QVBoxLayout()
        left2_layout = QVBoxLayout()
        center_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # ---- Left: TextBoxes ----
        self.log.printAndLogger("Initializing left panel textboxes")
        labels_textboxes = [
            (["Population Size", 100], "population_size"),
            (["NumEvals", 5000], "Num_Evaluations"),
            (["Studied", 5], "num_studied"),
            (["Total", 10], "total_num"),
            (["increase", 1], "increase"),
            #(["window", 1], "window"),
            (["Duration", "1 Y"], "duration"),
            
        ]

        self.textboxes = {}
        row1 = 0
        for label_text, key in labels_textboxes:
            label = QLabel(label_text[0])
            textbox = QLineEdit(str(label_text[1]))
            textbox.setFixedWidth(100)
            left_grid.addWidget(label, row1, 0)
            left_grid.addWidget(textbox, row1, 1)
            self.textboxes[key] = textbox
            row1 += 1

        labels_textboxes2 = [
            (["cr", 1], "cr"),
            (["f", 0.5], "f"),            
            (["Crossover Probability", 0.9], "crossoverProbability"),
            (["Crossover Distribution Index", 20], "crossoverDistributionIndex"),
            (["Mutation Distribution Index", 20], "mutationDistributionIndex"),
        ]

        row2 = 0
        for label_text, key in labels_textboxes2:
            label = QLabel(label_text[0])
            textbox = QLineEdit(str(label_text[1]))
            textbox.setFixedWidth(100)
            left_grid.addWidget(label, row2, 2)
            left_grid.addWidget(textbox, row2, 3)
            self.textboxes[key] = textbox
            row2 += 1

        # ---- Select directory ----
        """self.log.printAndLogger("Setting up directory selector")
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Download File Directory")
        self.dir_textbox = QLineEdit()
        dir_button = QPushButton("Select...")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_textbox)
        dir_layout.addWidget(dir_button)
        left_grid.addWidget(dir_label, row1, 0)
        left_grid.addLayout(dir_layout, row1, 1)"""

        # ---- Centro: Combos ----
        # Logging the initialization of dropdown elements
        self.log.printAndLogger("Setting up dropdowns")

        # Create label and dropdown for algorithm selection
        alg_label = QLabel("Algorithms")
        self.alg_combo = QComboBox()
        self.alg_combo.addItems(["MOEAD", "MOEADDE", "NSGAII", "SMPSO", "SMSEMOA"])  # Available optimization algorithms
        self.alg_combo.setFixedWidth(200)  # Set fixed width for consistency in UI
        center_layout.addWidget(alg_label)  # Add label to layout
        center_layout.addWidget(self.alg_combo)  # Add combo box to layout

        # Create label and dropdown for market selection
        markets_label = QLabel("Markets")
        self.markets_combo = QComboBox()
        self.markets_combo.addItems(["ALL", "AMEX", "ARCA", "BATS", "NASDAQ", "NYSE", "OTC"])  # List of market sources
        self.markets_combo.setFixedWidth(200)
        center_layout.addWidget(markets_label)
        center_layout.addWidget(self.markets_combo)

        # Create label and dropdown for frequency selection
        freq_label = QLabel("Frequencies")
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["Year", "Month", "Day"])  # Granularity of data frequency
        self.freq_combo.setCurrentText("Day")  # Default selection
        self.freq_combo.setFixedWidth(200)
        center_layout.addWidget(freq_label)
        center_layout.addWidget(self.freq_combo)

        # Create label and dropdown for window selection
        window_label = QLabel("window")
        self.window_combo = QComboBox()
        self.window_combo.addItems(["Year", "Month", "Day"])  # Time window for analysis
        self.window_combo.setFixedWidth(200)
        center_layout.addWidget(window_label)
        center_layout.addWidget(self.window_combo)
        # ---- Right Panel: Date pickers and Control Buttons ----

        self.log.printAndLogger("Configuring date pickers and control buttons")
        current_date = QDate.currentDate()

        # Label and date picker for the start date
        start_date_label = QLabel("Start")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)  # Enables calendar widget
        self.start_date.setFixedWidth(200)
        self.start_date.dateChanged.connect(self.on_date_start_changed)  # Connects change signal to handler
        self.start_date.setDate(current_date.addYears(-1))  # Default start date = one year ago
        self.start_pydate = self.start_date.date().toPyDate()  # Store as Python date

        # Label and date picker for the end date
        end_date_label = QLabel("End")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(200)
        self.end_date.setDate(current_date)  # Default end date = today
        self.end_pydate = self.end_date.date().toPyDate()
        self.end_date.dateChanged.connect(self.on_date_end_changed)  # Connect change signal

        # Button to update the list of assets
        self.assets_button = QPushButton("Update Assets List")
        self.assets_button.setFixedWidth(200)
        self.assets_button.setFixedHeight(40)

        # Button to download financial data
        self.download_button = QPushButton("Download Data")
        self.download_button.setFixedWidth(200)
        self.download_button.setFixedHeight(40)

        # Button to generate configuration files for JMetal algorithms
        self.JMetal_files_button = QPushButton("Generate JMetal Files")
        self.JMetal_files_button.setFixedWidth(200)
        self.JMetal_files_button.setFixedHeight(40)

        # Button to execute the selected optimization algorithm
        self.execAlg_button = QPushButton("Execute Algorithm")
        self.execAlg_button.setFixedWidth(200)
        self.execAlg_button.setFixedHeight(40)

        # Add all right-side widgets to the layout
        right_layout.addWidget(start_date_label)
        right_layout.addWidget(self.start_date)
        right_layout.addWidget(end_date_label)
        right_layout.addWidget(self.end_date)
        right_layout.addWidget(self.assets_button)
        right_layout.addWidget(self.download_button)        
        right_layout.addWidget(self.JMetal_files_button)
        right_layout.addWidget(self.execAlg_button)

        # ---- Add All Sub-Layouts to the Main Layout ----
        self.log.printAndLogger("Finalizing layout")
        controls_layout.addLayout(left_grid)
        controls_layout.addLayout(center_layout)
        controls_layout.addLayout(right_layout)
        main_layout.addWidget(controls_panel, stretch=1)

        # ---- Output Text Area ----
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)  # Read-only log console
        main_layout.addWidget(self.text_area, stretch=7)

        # ---- Horizontal Separator ----
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # ---- Progress Bar ----
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setHidden(True)
        self.progress_bar.setFormat("%v/%m")
        main_layout.addWidget(self.progress_bar)

        # ---- Initialization of Default Values and Signal Connections ----
        self.total_num = int(self.textboxes['total_num'].text())  # Total number of assets to process
        self.frequency = self.freq_combo.currentText()  # Selected data frequency
        self.window = self.window_combo.currentText()  # Window type (e.g., day, month)
        self.duration = self.textboxes['duration'].text()  # Paquete de datos descargados en cada consulta a través de IB
        self.default_download_dir = f"data\\financial_data\\IB_{self.frequency}"
        #self.dir_textbox.setText(self.default_download_dir)  # Show default path

        # Connect buttons to their respective handlers
        self.download_button.clicked.connect(self.download_data)
        self.assets_button.clicked.connect(self.update_assets)
        self.JMetal_files_button.clicked.connect(self.generate_JMetal_files)        
        self.execAlg_button.clicked.connect(self.execute_algorithm)

        self.log.printAndLogger("UI components initialized successfully")


    # Asociated function to the event of executing the evolutionary algorithm. execAlg_button
    def execute_algorithm(self):

        # Disable buttons and set styles button execute algorithm to orange
        self.JMetal_files_button.setEnabled(False)
        self.JMetal_files_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.execAlg_button.setEnabled(False)
        self.execAlg_button.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.assets_button.setEnabled(False)
        self.assets_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.download_button.setEnabled(False)
        self.download_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        QApplication.processEvents()  # Asegura que la UI se actualice

        """
        Execute the selected evolutionary algorithm with the specified parameters.
        This function constructs the command to run the algorithm using Java and the specified JAR file.
        """
        
        import subprocess
        start__date = datetime.now()

        # Path to the .jar file
        jar_path = ".\jar\portfolio-6.2.3-SNAPSHOT-jar-with-dependencies.jar"

        # Load the contents of the UI components into the variables to execute.
        population_size = self.textboxes['population_size'].text()
        num_studied = self.textboxes['num_studied'].text()
        total_num = self.textboxes['total_num'].text()
        frequency = self.freq_combo.currentText()
        markets_combo = self.markets_combo.currentText()
        increase = self.textboxes['increase'].text()
        #window = self.textboxes['window'].text()
        NumEvals = self.textboxes['Num_Evaluations'].text()
        cr = self.textboxes['cr'].text()
        f = self.textboxes['f'].text()
        alg_combo = self.alg_combo.currentText()
        
        # Main class and parameters
        main_class = f"org.uma.jmetal.portfolio.algorithm.{alg_combo}Example"
        dir_JMetal = "resources/JMetal_Files/"
        dir_Results = "Results/Individuals/"
        
        str_start_date_value = self.start_date.date().toString("yyyyMMdd")
        str_end_date_value = self.end_date.date().toString("yyyyMMdd")
        name_cov_file = f"_cov_hist_return_{markets_combo}_{num_studied}_{total_num}_{str_start_date_value}_{str_end_date_value}_.csv"
        self.log.printAndLogger("name_cov_file", name_cov_file)
        name_mean_file = f"_mean_hist_return_{markets_combo}_{num_studied}_{total_num}_{str_start_date_value}_{str_end_date_value}_.csv"
        self.log.printAndLogger("name_mean_file", name_mean_file)

        crossoverProbability = self.textboxes['crossoverProbability'].text()
        self.log.printAndLogger("crossoverProbability", crossoverProbability)
        crossoverDistributionIndex = self.textboxes['crossoverDistributionIndex'].text()
        self.log.printAndLogger("crossoverDistributionIndex", crossoverDistributionIndex)
        mutationDistributionIndex = self.textboxes['mutationDistributionIndex'].text()
        self.log.printAndLogger("mutationDistributionIndex", mutationDistributionIndex)
        
        if alg_combo == "MOEADDE":
            params = [
                dir_JMetal, population_size, markets_combo, num_studied, total_num, 
                "100", NumEvals, dir_Results, name_mean_file, name_cov_file,
                cr, f, mutationDistributionIndex
            ]
        elif alg_combo == "SMPSO":
            params = [
                dir_JMetal, population_size, markets_combo, num_studied, total_num, 
                "100", NumEvals, dir_Results, name_mean_file, name_cov_file
            ]
        else:
            params = [
                dir_JMetal, population_size, markets_combo, num_studied, total_num, 
                "100", NumEvals, dir_Results, name_mean_file, name_cov_file,
                crossoverProbability, crossoverDistributionIndex, mutationDistributionIndex
            ]

        # Construct the command
        cmd = ["java", "-cp", jar_path, main_class] + params
        
        self.log.printAndLogger("Executing command:")
        self.log.printAndLogger(cmd)

        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Display output and errors
        self.log.printAndLogger("STDOUT:\n", result.stdout)
        self.log.printAndLogger("STDERR:\n", result.stderr)

        end_date = datetime.now()
        file_directory = f"{dir_JMetal}Results/Individuals/{alg_combo}_{markets_combo}_{num_studied}_{total_num}"
        self.log.printAndLogger("File Directory", file_directory)
        result_file = self.existeArchivoResultado(file_directory, start__date, end_date)
        
        # Clear the text area
        self.text_area.clear()

        if result_file is not None:
            self.log.printAndLogger(f"File found: {result_file}")
            
            # Display the file content in the text area
            with open(result_file, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_area.setPlainText(content)
        else:
            # Display an error message if the file was not found
            self.text_area.setPlainText("Error finding the result file in the specified directory.")
            # Append the error message
            self.text_area.append(result.stderr)
        
        # Re-enable the buttons
        self.activate_buttons()

    # Function that extracts the result file after the execution of the evolutionary algorithm if it exists.
    def existeArchivoResultado(self, directorio, start__date, fecha_fin):

        print( directorio, start__date, fecha_fin)


        # Buscar archivos con prefijo 'result'
        archivos = glob.glob(os.path.join(directorio, 'results_*'))
        # Comprobación
        encontrado = False
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            
            # Obtener el timestamp de creación
            timestamp = os.path.getctime(archivo)

            # Convertir a formato legible
            fecha_archivo = datetime.fromtimestamp(timestamp)

            if start__date <= fecha_archivo <= fecha_fin:
                
                encontrado = True
                return archivo                
                break
            
        if not encontrado:
            print("File not found in the specified date range.")
        return None

    # Function to handle date changes in the start date picker
    def select_directory(self):
        """
        Open a dialog to select a directory and set the text in the directory textbox.
        This function allows the user to choose a directory for downloading files.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if directory:
            self.dir_textbox.setText(directory)

    # Function to update the list of assets
    def update_assets(self):
        """
            Update the list of assets by saving it to a CSV file, througt broker connection.
        """
        try:

            # Disable buttons and set styles button JMetal to orange
            self.JMetal_files_button.setEnabled(False)
            self.JMetal_files_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
            self.execAlg_button.setEnabled(False)
            self.execAlg_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
            self.assets_button.setEnabled(False)
            self.assets_button.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
            self.download_button.setEnabled(False)
            self.download_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
            QApplication.processEvents()  # Asegura que la UI se actualice

            
            control, self.df_Assets = self.assets_manager.save_assets_to_csv()
        
            if control:
                # Show a message box indicating success
                self.show_sms("Process OK", "¡Assets list correct updated!")
            else:
                self.show_sms("Incompleted Process", "¡ Assets list not updated! Check the log file for more details.")
        except Exception as e:
            # Show a message box indicating an error
            self.show_sms("Error", f"¡Error updating assets list! {str(e)}. \n Check {self.dir_data}Lib_Alpaca.json file is correctly configured.")
        
    # Function that connects to the JMetal Library and generates the JMetal files in a separate thread
    def generate_JMetal_files(self):

        # Disable buttons and set styles button JMetal to orange
        self.JMetal_files_button.setEnabled(False)
        self.JMetal_files_button.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.execAlg_button.setEnabled(False)
        self.execAlg_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.assets_button.setEnabled(False)
        self.assets_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.download_button.setEnabled(False)
        self.download_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        QApplication.processEvents()  # Asegura que la UI se actualice

        self.worker_JMetal = JMetalWorker.JMetalWorker(self)
        self.worker_JMetal.finished.connect(self.on_finished)
        self.worker_JMetal.start()

    # Function that connects to the JMetal Library and generates the JMetal files
    def run_jmetal_logic(self):

        if not self.dir_data is None or self.dir_data != "":
            self.df_Assets = self.assets_manager.load_assets_from_csv()

        if len(self.df_Assets) > 0:
            
            self.selectAssets(considerSizes=True)

            population_size = int(self.textboxes['population_size'].text())
            num_studied = int(self.textboxes['num_studied'].text())
            total_num = int(self.textboxes['total_num'].text())
            frequency = self.freq_combo.currentText()
            markets_combo = self.markets_combo.currentText()
            increase = int(self.textboxes['increase'].text())
            
            self.log.printAndLogger(f"population_size: {population_size}")
            self.log.printAndLogger(f"num_studied: {num_studied}")
            self.log.printAndLogger(f"total_num: {total_num}")
            self.log.printAndLogger(f"frequency: {frequency}")
            self.log.printAndLogger(f"markets_combo: {markets_combo}")
            self.log.printAndLogger(f"increase: {increase}")

            fechaInicio_dt = datetime(self.start_pydate.year, self.start_pydate.month, self.start_pydate.day, 0, 0, 0)
            fechaFin_dt = datetime(self.end_pydate.year, self.end_pydate.month, self.end_pydate.day, 0, 0, 0)
            
            jmetal = genArch_JMetal.GenerateStatisticalFilesJMetal(
                population_size=population_size,
                num_est=num_studied,
                num_tot=total_num,
                directory=self.default_download_dir,
                start_date=fechaInicio_dt,
                end_date=fechaFin_dt,
                class_assets="",
                exchange=markets_combo,
                increase_freq="year",
                increase=increase,
                window_freq="year",
                window=1,
                frequency=frequency,
                df_assets=self.df_Assets
            )
            
        else:
            
            self.activate_buttons()

    # Function to be called when the worker thread finishes
    def on_finished(self):
        # Re-enable the buttons
        self.activate_buttons()
    
    # Re-enable the buttons
    def activate_buttons(self):
        # Re-enable the buttons
        self.JMetal_files_button.setEnabled(True)
        self.JMetal_files_button.setStyleSheet("")  # <- This clears the style and returns to the default system appearance
        self.execAlg_button.setEnabled(True)
        self.execAlg_button.setStyleSheet("")  # <- This clears the style and returns to the default system appearance
        self.assets_button.setEnabled(True)
        self.assets_button.setStyleSheet("")  # <- This clears the style and returns to the default system appearance
        self.download_button.setEnabled(True)
        self.download_button.setStyleSheet("")  # <- This clears the style and returns to the default system appearance
   
    # Select the assets to be studied.
    def selectAssets(self, considerSizes=False):
        
        self.log.printAndLogger("selectAssets  --  considerSizes:", considerSizes)
        
        self.df_Assets = self.df_Assets[self.df_Assets['class'] == 'us_equity']
        #self.df_Assets = self.df_Assets[self.df_Assets['fractionable'] == True]
        self.df_Assets = self.df_Assets[self.df_Assets['status'] == 'active']
        
        # Seleccionamos el mercado a estudiar.
        self.selected_market = self.markets_combo.currentText()
        if self.selected_market.upper() != "ALL":
            self.df_Assets = self.df_Assets[self.df_Assets.exchange == self.selected_market]    

        # Número total de activos a evaluar.
        self.total_num = int(self.textboxes['total_num'].text())
        self.frequency = self.freq_combo.currentText()
        self.window = self.window_combo.currentText()
        self.duration = self.textboxes['duration'].text()
        
        # Convertir QDate a datetime
        fechaInicio_dt = datetime(self.start_pydate.year, self.start_pydate.month, self.start_pydate.day, 0, 0, 0)
        fechaFin_dt = datetime(self.end_pydate.year, self.end_pydate.month, self.end_pydate.day, 0, 0, 0)
        
        if considerSizes:
            self.df_Assets = self.get_top_files(self.default_download_dir, self.df_Assets, fechaInicio_dt, fechaFin_dt, self.total_num)
        else:
            self.df_Assets = self.df_Assets[:self.total_num]   

    # Function to handle date changes in the start date picker
    def get_top_files(self, default_download_dir, df_Assets, fechaInicio, fechaFin, n):
        
        top_files = []

        # frequency: get the frequency selected by the user in the combo box.
        frequency = self.freq_combo.currentText()        # File_Name: Generate the filename to search for each asset.
        df_Assets['Nombre_Archivo'] = df_Assets['symbol'].astype(str).apply(lambda x: f"{frequency}_{x}_.csv")
        
        # Filter assets that don't have the expected filename
        files = list(self.get_path_files(df_Assets, 'Nombre_Archivo', default_download_dir).values())

        num_records_max = 0
        
        for file in files:
            try:
                self.log.printAndLogger(f" File {file}")
                df = pd.read_csv(file, header=0, encoding='utf-8', parse_dates=[0], index_col=[0], date_parser=lambda x: pd.to_datetime(x.rpartition('+')[0]))
                df.index = pd.to_datetime(df.index)  # Convert to datetime index
                df = df.loc[~df.index.duplicated()]  # Remove duplicated indices
                df_filtrado = df[(df.index >= fechaInicio) & (df.index <= fechaFin)]
                num_records = len(df_filtrado)
                
                if num_records > num_records_max:
                    num_records_max = num_records
                # Insert in sorted order if it's better than some existing or list is not full
                if len(top_files) < n:
                    self.log.printAndLogger("   Adding to top files")
                    top_files.append((file, num_records))
                    top_files.sort(key=lambda x: x[1], reverse=True)
                elif num_records > top_files[-1][1]:
                    self.log.printAndLogger("   Replacing top file")
                    top_files[-1] = (file, num_records)
                    top_files.sort(key=lambda x: x[1], reverse=True)

                # Early stopping condition if all top n files have high record count
                if len(top_files) == n and all(f[1] >= num_records_max - (num_records_max * 0.1) for f in top_files):
                    self.log.printAndLogger("Early stopping condition reached.")
                    break
                
            except Exception as e:
                self.log.printAndLogger(f"Error processing {file}: {e}")
                continue

        elementos = [os.path.basename(f[0]) for f in top_files]
        df_Assets = df_Assets[df_Assets['Nombre_Archivo'].isin(elementos)]
        
        return df_Assets

    # Function to get the full paths of files based on names in a DataFrame column
    def get_path_files(self, df, columna_archivo, carpeta):
        """
        Searches for files in the specified folder according to names in a DataFrame column.

        :param df: DataFrame with file names
        :param columna_archivo: Column name that contains the filenames
        :param carpeta: Path to the folder where files should be located
        :return: Dictionary {filename: full_path} if file exists
        """
        rutas = {}
        for nombre_archivo in df[columna_archivo].dropna().unique():  # Remove NaNs and duplicates
            ruta_completa = os.path.join(carpeta, nombre_archivo)
            if os.path.isfile(ruta_completa):
                rutas[nombre_archivo] = ruta_completa
        return rutas

    # Function to download data from the broker
    def download_data(self):
        
        """
        Function that connects to the broker and downloads financial data for the asset list.
        """

        # Disable buttons and set styles button download to orange
        self.JMetal_files_button.setEnabled(False)
        self.JMetal_files_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.execAlg_button.setEnabled(False)
        self.execAlg_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.assets_button.setEnabled(False)
        self.assets_button.setStyleSheet("background-color: silver; color: black; font-weight: bold;")
        self.download_button.setEnabled(False)
        self.download_button.setStyleSheet("background-color: orange; color: white; font-weight: bold;")


        # Check if the directory is set
        if not self.dir_data is None or self.dir_data != "":
            # Load the asset list from the CSV file
            self.df_Assets = self.assets_manager.load_assets_from_csv()

        # Check if the asset list is loaded and has data
        if not self.df_Assets is None and len(self.df_Assets) > 0:

            # Select assets based on the current configuration
            self.selectAssets()

            # If there are assets to process
            if len(self.df_Assets) > 0:

                # Set maximum value for progress bar
                self.progress_bar.setMaximum(len(self.df_Assets))
                # Make progress bar visible
                self.progress_bar.setHidden(False)

                cont = 0
                self.progress_bar.setValue(cont)

                # Background process to download data without blocking the UI
                self.worker_IB = IB_data_loader.HistoricalDataWorker(self.df_Assets, self.duration, self.end_pydate, self.frequency, self.log)
                self.worker_IB.data_ready.connect(self.display_data)
                self.worker_IB.error_signal.connect(self.show_error)
                self.worker_IB.update_progress.connect(self.update_progress)
                self.worker_IB.finished.connect(self.on_finished)
                self.worker_IB.start()

                cont += 1

            # Capture values from QLineEdit
            textbox_values = {key: textbox.text() for key, textbox in self.textboxes.items()}

            # Capture selected dates from QDateEdit
            start_date_value = self.start_date.date().toString("yyyy-MM-dd")
            end_date_value = self.end_date.date().toString("yyyy-MM-dd")

            # Show captured values in the console (or perform another action with them)
            self.log.printAndLogger("Selected values:")
            self.log.printAndLogger(f" Market: {self.selected_market}")
            self.log.printAndLogger(f" Frequency: {self.frequency}")
            self.log.printAndLogger(f" Window: {self.window}")
            self.log.printAndLogger(f" Dates: Start = {start_date_value}, End = {end_date_value}")
            self.log.printAndLogger(f" TextBox values:", textbox_values)
            self.log.printAndLogger(f" total_num: {self.total_num}")
            self.log.printAndLogger(f" duration: {self.duration}")

            # Simulate long process using a QTimer (optional)
            """
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_progress)
            self.timer.start(100)  # Call every 100 ms
            """
        else:
            self.show_sms("No asset list found to download.", "You must select the directory containing the asset list file.")

    # Function to update the progress bar
    def update_progress(self):
        """
        This function updates the progress bar.
        """
        # Get the current value of the progress bar and increment it
        current_value = self.progress_bar.value()
        # Increment the progress bar value by 1
        self.progress_bar.setValue(current_value + 1)
        
    # Function to show messages in a message box
    def show_sms(self, titulo, mensaje):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Information if "Process OK" in titulo else QMessageBox.Critical)
        msg_box.exec_()

        self.activate_buttons()

    # Function to handle date changes in the end date picker
    def on_date_end_changed(self):
        # self.end_pydate = self.date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.end_pydate = self.end_date.date().toPyDate()
        # self.label.setText(f"Selected date: {fecha}")
        print("Selected end_date:", self.end_pydate)

    # Function to handle date changes in the start date picker
    def on_date_start_changed(self):
        # self.end_pydate = self.date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.start_pydate = self.start_date.date().toPyDate()
        # self.label.setText(f"Selected date: {fecha}")
        print("Selected start_date:", self.start_pydate)

    # Function to display data in the text area after downloading
    def display_data(self, data):
        print("Finish")
        print(data)

    # Function to show error messages in a message box
    def show_error(self, error_msg):
        # self.label.setText(f"Error: {error_msg}")
        # print(f"Error: {error_msg}")
        self.log.printAndLogger(error_msg)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setText(error_msg + "\n Check Gateway IB is running and connected.")
        msg_box.setIcon(QMessageBox.Information if "Correct" in error_msg else QMessageBox.Critical)
        msg_box.exec_()

#   Main function to run the application
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
