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

"""def main(log):
    
    # Main entry point for the application.
    
    log.printAndLogger(" main - Main entry point for the application.")

    # Si estamos en CI (GitHub Actions, Docker, etc.), desactivar GUI
    if os.environ.get("CI", "").lower() in ["true", "1"] or os.environ.get("GITHUB_ACTIONS", "").lower() in ["true", "1"]:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    
    # Set custom styles if available
    try:
        with open("resources/styles.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        log.printAndLogger("Style file not found. Using default styles.")
    
    ## Mostrar la ventana solo si no estamos en CI
    if not (os.environ.get("CI", "").lower() in ["true", "1"] or os.environ.get("GITHUB_ACTIONS", "").lower() in ["true", "1"]):        
        # Create and show the main window
        main_window = MainWindow(log)
        main_window.show()
        sys.exit(app.exec())
    else:
        print("Running in CI environment — GUI not executed.")"""

def main(log):
    """
    Main entry point for the application.
    """
    log.printAndLogger(" main - Main entry point for the application.")

    is_ci = os.environ.get("CI", "").lower() in ["true", "1"] or \
            os.environ.get("GITHUB_ACTIONS", "").lower() in ["true", "1"]

    if is_ci:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        print("Running in CI environment — GUI not executed.")
        return  # 👈 Salir aquí, sin crear QApplication ni MainWindow

    # --- Solo se ejecuta fuera de CI ---
    app = QApplication(sys.argv)

    try:
        with open("resources/styles.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        log.printAndLogger("Style file not found. Using default styles.")

    main_window = MainWindow(log)
    main_window.show()
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
