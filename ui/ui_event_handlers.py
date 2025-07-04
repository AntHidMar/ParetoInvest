from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QCheckBox, QDateEdit, QFrame, QTextEdit,
                             QProgressBar, QShortcut)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QDate
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
    print("on_finished")
    # Re-enable the buttons
    self.activate_buttons()


# Function to handle changes in the checkbox state for updating asset types
def checkbox_types_changed(self, state):
    """
    Function to handle changes in the checkbox state for updating asset types.        
    """
    self.checkbox_types_state = not self.checkbox_types_state
    if state == Qt.Checked:
        self.log.printAndLogger("Checkbox 'Update Types' checked.")
    else:
        self.log.printAndLogger("Checkbox 'Update Types' unchecked.")

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

def show_checkbox(self):
    """
    Function to show the checkbox for updating asset types when the user presses Ctrl+H+I.
    """
    self.checkbox_types.setVisible(True)
    self.checkbox_types_state = True
    self.checkbox_types.setChecked(self.checkbox_types_state)
    self.log.printAndLogger("Checkbox 'Update Types' shown.")

def hide_checkbox(self):
    """
    Function to hide the checkbox for updating asset types when the user presses Ctrl+H+I.
    """
    self.checkbox_types.setVisible(False)
    self.checkbox_types_state = False
    self.checkbox_types.setChecked(self.checkbox_types_state)
    self.log.printAndLogger("Checkbox 'Update Types' hidden.")  


# Function to display data in the text area after downloading
def display_data(self, data):
    
    self.log.printAndLogger(data)