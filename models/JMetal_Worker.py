from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime


class JMetalWorker(QThread):
    finished = pyqtSignal()
    show_sms = pyqtSignal(str, str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        # Run the JMetal logic
        self.parent.run_jmetal_logic()        
        # Emit a message indicating the process is OK
        self.show_sms.emit("Process OK", "JMetal files generated successfully")
        # Emit the finished signal
        self.finished.emit()

        