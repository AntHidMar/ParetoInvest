# ui_components.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QCheckBox, QDateEdit, QFrame, QTextEdit,
                             QProgressBar)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QKeySequence, QShortcut

import ParetoInvest.ui.ui_event_handlers as ui_event_handlers

# Definition UI components
def init_ui(self, log):

    log.printAndLogger("Initializing UI components")

    # Create a central widget
    central_widget = QWidget(self)
    self.setCentralWidget(central_widget)

    # Create a main layout
    main_layout = QVBoxLayout()
    central_widget.setLayout(main_layout)

    # Create a panel (QFrame) for the top controls
    controls_panel = QFrame()
    #controls_panel.setFrameShape(QFrame.StyledPanel)    
    controls_panel.setFrameShape(QFrame.Shape.StyledPanel)
    controls_layout = QHBoxLayout(controls_panel)

    # ---- Layouts inside the panel ----
    log.printAndLogger("Creating internal layouts")
    self.grid_problem = QGridLayout()
    self.grid_algs = QGridLayout()
    left_layout = QVBoxLayout()
    left2_layout = QVBoxLayout()
    center_layout = QVBoxLayout()
    right_layout = QVBoxLayout()

    # ---- Left: TextBoxes ----
    log.printAndLogger("Initializing left panel textboxes")
    labels_textboxes_problem = [
        (["Population Size", 100], "population_size"),
        (["NumEvals", 5000], "Num_Evaluations"),
        (["Studied", 5], "num_studied"),
        (["Total", 10], "total_num"),
        (["increase", 1], "increase"),
        #(["window", 1], "window"),
        (["Duration", "1 Y"], "duration"),
        (["Seed", 0], "seed"),
        
    ]

    self.textboxes_problem = {}
    row1 = 0
    for label_text, key in labels_textboxes_problem:
        label = QLabel(label_text[0])
        textbox = QLineEdit(str(label_text[1]))
        textbox.setFixedWidth(100)
        self.grid_problem.addWidget(label, row1, 0)
        self.grid_problem.addWidget(textbox, row1, 1)
        self.textboxes_problem[key] = textbox
        row1 += 1

    self.components_algs = {}
    options_textboxes_algs = [
        (["Selection", ['tournament','random'], ["NSGAII"]], "selection"),
        (["TournamentSize", 2, ["NSGAII"]], "tournamentSize"),
        (["Crossover", ['SBX'], ["NSGAII","SMSEMOA"]], "crossover"),
        (["Crossover", ['SBX','DE'], ["MOEAD","MOEADDE"]], "crossover"),  
        (["Crossover Probability", 0.9, ["NSGAII","MOEAD","SMSEMOA"]], "crossoverProbability"),
        (["Crossover Distribution Index", 20, ["NSGAII","MOEAD","SMSEMOA"]], "crossoverDistributionIndex"),
        (["cr", 1, ["MOEAD","MOEADDE"]], "cr"),
        (["f", 0.5, ["MOEAD","MOEADDE"]], "f"),            
        (["Neighborhood Selection Probability", 0.5, ["MOEAD","MOEADDE"]], "neighborhoodSelectionProbability"),    
        (["Neighborhood Size", 50, ["MOEAD","MOEADDE"]], "neighborhoodSize"),    
        (["functionType", ['PBI'], ["MOEAD","MOEADDE"]], "functionType"),    
        (["Aggregation Penalty", 0.1, ["MOEAD","MOEADDE"]], "aggregationPenalty"),    
        (["Normalize Objectives", ['True','False'], ["MOEAD","MOEADDE"]], "normalizeObjectives"),  
        (["Max Replaced Solutions", 1, ["MOEAD","MOEADDE"]], "maxReplacedSolutions"),
        (["Hyper Volume Offset", 0.5, ["SMSEMOA"]], "hypervolumeOffset"),
        (["C1", 0.5, ["SMPSO"]], "c1"),
        (["C2", 0.5, ["SMPSO"]], "c2"),
        (["Inertia Weight", 1, ["SMPSO"]], "inertiaWeight"),
        (["Velocity Constriction", 0.5, ["SMPSO"]], "velocityConstriction"),
        (["Mutation", ['Polinomial'], ["NSGAII","MOEAD","MOEADDE","SMPSO","SMSEMOA"]], "mutation"),
        (["Mutation Distribution Index", 50, ["NSGAII","MOEAD","MOEADDE","SMPSO","SMSEMOA"]], "mutationDistributionIndex"),
        (["Mutation Repair", ['random','round','bounds'], ["NSGAII","MOEAD","MOEADDE","SMPSO","SMSEMOA"]], "mutationRepair"),        
    ]

    

    # ---- Centro: Combos ----
    # Logging the initialization of dropdown elements
    log.printAndLogger("Setting up dropdowns")

    # Create label and dropdown for algorithm selection
    self.alg_label = QLabel("Algorithms")
    self.alg_layout = QHBoxLayout()
    self.alg_combo = QComboBox()
    self.alg_combo.addItems(["MOEAD", "MOEADDE", "NSGAII", "SMPSO", "SMSEMOA"])     # Available optimization algorithms
    self.alg_combo.setFixedWidth(200)                                               # Set fixed width for consistency in UI
    self.alg_layout.addWidget(self.alg_label)
    self.alg_layout.addWidget(self.alg_combo)
    center_layout.addLayout(self.alg_layout)
    self.alg_combo.currentIndexChanged.connect(lambda index: ui_event_handlers.on_algorithm_changed(self, options_textboxes_algs))    
    ui_event_handlers.on_algorithm_changed(self, options_textboxes_algs)            # Call event first time.
    
    # Create label and dropdown for market selection
    markets_label = QLabel("Markets")
    self.mar_layout = QHBoxLayout()
    self.markets_combo = QComboBox()
    if (self.df_Assets is not None and not self.df_Assets.empty and "exchange" in self.df_Assets.columns and self.df_Assets["exchange"].notna().any()):
        mercados = sorted(self.df_Assets["exchange"].dropna().unique().tolist())
        self.markets_combo.addItems(["ALL"] + mercados)
    else:
        self.markets_combo.addItems(["ALL"])
    #self.markets_combo.addItems(["ALL"] + list(self.df_Assets.exchange.unique()))  # List of market sources
    self.markets_combo.setFixedWidth(200)
    self.mar_layout.addWidget(markets_label)
    self.mar_layout.addWidget(self.markets_combo)
    center_layout.addLayout(self.mar_layout)

    # Asset Type
    type_label = QLabel("type")
    self.type_combo = QComboBox()
    if (self.df_Assets is not None and not self.df_Assets.empty and "asset_type" in self.df_Assets.columns and self.df_Assets["asset_type"].notna().any()):
        types = sorted(self.df_Assets["asset_type"].dropna().unique().tolist())
        self.type_combo.addItems(["ALL"] + types)
    else:
        self.type_combo.addItems(["ALL"])
    #self.type_combo.addItems(["ALL"] +  list(self.df_Assets.asset_type.unique()))
    self.type_combo.setFixedWidth(200)
    self.type_layout = QHBoxLayout()
    self.type_layout.addWidget(type_label)
    self.type_layout.addWidget(self.type_combo)
    center_layout.addLayout(self.type_layout)
    
    # Asset sector
    sector_label = QLabel("sector")
    self.sector_combo = QComboBox()
    if (self.df_Assets is not None and not self.df_Assets.empty and "FMP_sector" in self.df_Assets.columns and self.df_Assets["FMP_sector"].notna().any()):
        sectores = sorted(self.df_Assets["FMP_sector"].dropna().unique().tolist())        
        self.sector_combo.addItems(["ALL"] + sectores)
    else:
        self.sector_combo.addItems(["ALL"])    
    self.sector_combo.setFixedWidth(200)
    self.sector_layout = QHBoxLayout()
    self.sector_layout.addWidget(sector_label)
    self.sector_layout.addWidget(self.sector_combo)
    center_layout.addLayout(self.sector_layout)

    # Create label and dropdown for frequency selection
    freq_label = QLabel("Frequencies")
    self.freq_combo = QComboBox()
    self.freq_combo.addItems(["Year", "Month", "Day", "Hour", "Minute", "Second"])  # Granularity of data frequency
    self.freq_combo.setCurrentText("Day")  # Default selection
    self.freq_combo.setFixedWidth(200)
    self.freq_layout = QHBoxLayout()
    self.freq_layout.addWidget(freq_label)
    self.freq_layout.addWidget(self.freq_combo)
    center_layout.addLayout(self.freq_layout)

    # Create label and dropdown for window selection
    window_label = QLabel("windows")
    self.window_combo = QComboBox()
    self.window_combo.addItems(["Year", "Month", "Day"])  # Time window for analysis
    self.window_combo.setFixedWidth(200)
    self.window_layout = QHBoxLayout()
    self.window_layout.addWidget(window_label)
    self.window_layout.addWidget(self.window_combo)
    center_layout.addLayout(self.window_layout)

    log.printAndLogger("Configuring date pickers and control buttons")
    current_date = QDate.currentDate()

    # Label and date picker for the start date
    start_date_label = QLabel("Start")
    self.start_date = QDateEdit()
    self.start_date.setCalendarPopup(True)  # Enables calendar widget
    self.start_date.setFixedWidth(200)
    self.start_date.dateChanged.connect(lambda: ui_event_handlers.on_date_start_changed(self))  # Connects change signal to handler
    self.start_date.setDate(current_date.addYears(-1))  # Default start date = one year ago
    self.start_pydate = self.start_date.date().toPyDate()  # Store as Python date

    # Label and date picker for the end date
    end_date_label = QLabel("End")
    self.end_date = QDateEdit()
    self.end_date.setCalendarPopup(True)
    self.end_date.setFixedWidth(200)
    self.end_date.setDate(current_date)  # Default end date = today
    self.end_pydate = self.end_date.date().toPyDate()
    self.end_date.dateChanged.connect(lambda: ui_event_handlers.on_date_end_changed(self))  # Connect change signal

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

    # Generate checkboxes for allow user to update assets types
    self.checkbox_types_state = False
    self.checkbox_types = QCheckBox("Update Types")
    self.checkbox_types.stateChanged.connect(lambda state: ui_event_handlers.checkbox_types_changed(self, state))    
    self.checkbox_types.setChecked(self.checkbox_types_state)  # Set initial state of checkbox
    self.checkbox_types.setVisible(False)

    # shortcut: Ctrl+S+F to show/hide the checkbox
    self.shortcut_show_cb = QShortcut(QKeySequence("Ctrl+S"), self)
    self.shortcut_show_cb.activated.connect(lambda: ui_event_handlers.show_checkbox(self))
    
    # shortcut: Ctrl+S+H to hide the checkbox
    self.shortcut_hide_cb = QShortcut(QKeySequence("Ctrl+H"), self)
    self.shortcut_hide_cb.activated.connect(lambda: ui_event_handlers.hide_checkbox(self))

    # Add all right-side widgets to the layout
    right_layout.addWidget(start_date_label)
    right_layout.addWidget(self.start_date)
    right_layout.addWidget(end_date_label)
    right_layout.addWidget(self.end_date)
    right_layout.addWidget(self.assets_button)
    right_layout.addWidget(self.checkbox_types)  # Add checkbox for updating asset types
    right_layout.addWidget(self.download_button)        
    right_layout.addWidget(self.JMetal_files_button)
    right_layout.addWidget(self.execAlg_button)

    # ---- Add All Sub-Layouts to the Main Layout ----
    log.printAndLogger("Finalizing layout")
    controls_layout.addLayout(self.grid_problem)
    controls_layout.addLayout(self.grid_algs)
    controls_layout.addLayout(center_layout)
    controls_layout.addLayout(right_layout)
    main_layout.addWidget(controls_panel, stretch=1)

    # ---- Output Text Area ----
    self.text_area = QTextEdit(self)
    self.text_area.setReadOnly(True)  # Read-only log console
    main_layout.addWidget(self.text_area, stretch=7)

    # ---- Horizontal Separator ----
    separator = QFrame()
    #separator.setFrameShape(QFrame.HLine)
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
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
    self.total_num = int(self.textboxes_problem['total_num'].text())  # Total number of assets to process
    self.frequency = self.freq_combo.currentText()  # Selected data frequency
    self.window = self.window_combo.currentText()  # Window type (e.g., day, month)
    self.duration = self.textboxes_problem['duration'].text()  # Paquete de datos descargados en cada consulta a través de IB
    self.default_download_dir = f"data\\financial_data\\IB_{self.frequency}"
    #self.dir_textbox.setText(self.default_download_dir)  # Show default path

    # Connect buttons to their respective handlers
    self.download_button.clicked.connect(self.download_data)
    self.assets_button.clicked.connect(self.update_assets)
    self.JMetal_files_button.clicked.connect(self.generate_JMetal_files)        
    self.execAlg_button.clicked.connect(self.execute_algorithm)

    log.printAndLogger("UI components initialized successfully")

