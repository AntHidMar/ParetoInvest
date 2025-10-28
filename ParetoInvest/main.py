import os, sys

from PyQt6.QtWidgets import QApplication

# --- Detectin if executing from .exe or from Python ---
if getattr(sys, 'frozen', False):
    # exe (PyInstaller)
    base_path = sys._MEIPASS
    project_root = os.path.dirname(sys.executable)    
else:
    # Developing
    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_path)

# Añadimos el paquete principal y raíz del proyecto al sys.path
if base_path not in sys.path:
    sys.path.append(base_path)
if project_root not in sys.path:
    sys.path.append(project_root)

from ParetoInvest.ui.main_window import MainWindow
import ParetoInvest.libraries.Lib_Logger as lib_Logger

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
    sys.exit(app.exec())

if __name__ == "__main__":
    
    # Create the logger instance
    log = lib_Logger.Logger()
    
    """#prefix = 'a'       -- Assets starting with 'a'
    prefix = sys.argv[1]
    clientId = sys.argv[2]
    eliminarFichero = int(sys.argv[3])"""

    # Main function
    main(log)
