import os
import logging
from datetime import datetime
import inspect

class Logger:

    def __init__(self, nombre=None, sufijo=""):
        # Initialize the log filename suffix and directory
        self._sufijo = sufijo
        self._dirLOG = "LOG"

        # Get the name of the executing script if not provided
        self._nombre = nombre or self._get_current_script_name()

        # Create and configure the logger
        self._logger = logging.getLogger(self._nombre)
        self._logger.setLevel(logging.DEBUG)

        # Initialize the file handler for the logger
        self._file_handler = None
        self._set_file_handler()

    def _set_file_handler(self):
        """Set up the FileHandler for logging using the current script name."""
        # Format the log file name with date and suffix
        fecha_dia_log = datetime.now().strftime('%Y_%m_%d')
        log_file = os.path.join(self._dirLOG, f'{self._nombre}_{fecha_dia_log}_{self._sufijo}.log')

        # Remove any existing handlers to avoid duplicate logs
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
            handler.close()

        # Create and configure the new file handler
        self._file_handler = logging.FileHandler(log_file)
        self._file_handler.setLevel(logging.DEBUG)

        # Set the log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._file_handler.setFormatter(formatter)

        # Add the new handler to the logger
        self._logger.addHandler(self._file_handler)
        # Optionally prevent log propagation to the root logger
        # self._logger.propagate = False

    def _get_current_script_name(self):
        """Get the name of the executing script without its extension."""
        frame = inspect.stack()[-1]  # Access the last frame in the stack (main script)
        script_path = frame.filename
        return os.path.splitext(os.path.basename(script_path))[0]

    def set_nombre(self, nuevo_nombre):
        """Change the logger name and reconfigure the log file."""
        if nuevo_nombre != self._nombre:
            self._nombre = nuevo_nombre
            self._logger.name = nuevo_nombre  # Update logger name
            self._set_file_handler()  # Reinitialize file handler with new name

    def update_father_file():
        """Update the logger name based on the calling (parent) file."""
        # This method is not working because it lacks 'self' argument
        parent_file = inspect.stack()[1].filename
        parent_name = os.path.splitext(os.path.basename(parent_file))[0]

        self._nombre = parent_name
        self._logger.name = self._nombre  # Update logger name
        self._set_file_handler()  # Reinitialize file handler with new name

    def printAndLogger(self, cadena, tipo=0):
        """
        Print and/or log the provided message based on type:
        tipo=0: print and log
        tipo=1: only print
        tipo=2: only log
        """
        if tipo == 0 or tipo == 1:
            print(cadena)
        if tipo == 0 or tipo == 2:
            self._logger.info(cadena)

    @property
    def logger(self):
        """Expose the internal logger object."""
        return self._logger
