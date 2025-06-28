import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
import libraries.Lib_Logger as lib_Logger

def main(log):
    """
    Main entry point for the application.
    """
    log.printAndLogger(" main - Main entry point for the application.")

    # Create an instance of QApplication
    app = QApplication(sys.argv)
    
    # Set custom styles if available
    try:
        with open("resources/styles.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        log.printAndLogger("Style file not found. Using default styles.")
    
    # Create and show the main window
    main_window = MainWindow(log)
    main_window.show()
    
    # Run the application's main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    
    # Create the logger instance
    log = lib_Logger.Logger()
    
    """#prefix = 'a'       -- Assets starting with 'a'
    prefix = sys.argv[1]
    clientId = sys.argv[2]
    eliminarFichero = int(sys.argv[3])"""

    # Main function
    main(log)
