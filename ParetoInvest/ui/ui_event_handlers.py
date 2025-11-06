from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QCheckBox, QDateEdit, QFrame, QTextEdit,
                             QProgressBar, QListWidgetItem, QListWidget)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QDate
### Events ###


# Event to update the progress bar
def update_progress(self):
    """
    This function updates the progress bar.
    """
    # Get the current value of the progress bar and increment it
    current_value = self.progress_bar.value()
    # Increment the progress bar value by 1
    self.progress_bar.setValue(current_value + 1)

# Function to be called when the worker thread finishes
def on_finished(self):
    # Re-enable the buttons
    self.activate_buttons()

# Function to handle changes in the checkbox state for updating asset types
def checkbox_types_changed(self, state):
    """
    Function to handle changes in the checkbox state for updating asset types.        
    """    
    # Qt.Checked -> 2, Qt.Unchecked -> 0
    if state == 2:
        self.checkbox_types_state = True
        self.log.printAndLogger("Checkbox 'Update Types' checked.")
    else:
        self.checkbox_types_state = False
        self.log.printAndLogger("Checkbox 'Update Types' unchecked.")

def show_checkbox(self):
    """
    Function to show the checkbox for updating asset types when the user presses Ctrl+H+I.
    """
    self.checkbox_types.setVisible(True)
    self.log.printAndLogger("Checkbox 'Update Types' shown.")

def hide_checkbox(self):
    """
    Function to hide the checkbox for updating asset types when the user presses Ctrl+H+I.
    """
    self.checkbox_types.setVisible(False)
    self.log.printAndLogger("Checkbox 'Update Types' hidden.")  
    
# Function to handle date changes in the end date picker
def on_date_end_changed(self):
    self.end_pydate = self.end_date.date().toPyDate()

# Function to handle date changes in the start date picker
def on_date_start_changed(self):
    self.start_pydate = self.start_date.date().toPyDate()

# Function to display data in the text area after downloading
def display_data(self, data):    
    self.log.printAndLogger(data)

def clear_layout(layout):
    """Elimina todos los widgets de un layout de forma segura."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            # Si el item es un sublayout, lo limpiamos recursivamente
            sublayout = item.layout()
            if sublayout is not None:
                clear_layout(sublayout)

def on_algorithm_changed(self, options_textboxes_algs):

    selected_algorithm = self.alg_combo.currentText()
    print(f"Selected algorithm: {selected_algorithm}")

    clear_layout(self.grid_algs)
    self.components_algs.clear()

    row2 = 0
    for options, key in options_textboxes_algs:

        textbox_label = QLabel(options[0])        
        textbox_algs = options[2]

        value = options[1]
        if isinstance(value, (int, float, str)):
            textbox_values = QLineEdit(str(value))
        elif isinstance(value, (list, tuple)):
            textbox_values = QComboBox()
            textbox_values.addItems([str(v) for v in value])
        else:
            textbox_values = QLineEdit(str(value))

        if selected_algorithm in textbox_algs:
            textbox_values.setFixedWidth(100)
            self.grid_algs.addWidget(textbox_label, row2, 2)
            self.grid_algs.addWidget(textbox_values, row2, 3)
            self.components_algs[key] = textbox_values
            row2 += 1