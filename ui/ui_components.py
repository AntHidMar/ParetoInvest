# ui_components.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QCheckBox, QDateEdit, QFrame, QTextEdit,
                             QProgressBar, QShortcut)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QKeySequence

import ui.ui_event_handlers as ui_event_handlers

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
    controls_panel.setFrameShape(QFrame.StyledPanel)
    controls_layout = QHBoxLayout(controls_panel)

    # ---- Layouts inside the panel ----
    log.printAndLogger("Creating internal layouts")
    left_grid = QGridLayout()
    left_layout = QVBoxLayout()
    left2_layout = QVBoxLayout()
    center_layout = QVBoxLayout()
    right_layout = QVBoxLayout()

    # ---- Left: TextBoxes ----
    log.printAndLogger("Initializing left panel textboxes")
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
    """log.printAndLogger("Setting up directory selector")
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
    log.printAndLogger("Setting up dropdowns")

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
    self.checkbox_types.setChecked(self.checkbox_types_state)  # Set initial state of checkbox
    self.checkbox_types.stateChanged.connect(lambda state: ui_event_handlers.checkbox_types_changed(self, state))
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

    log.printAndLogger("UI components initialized successfully")

