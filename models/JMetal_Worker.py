from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime


class JMetalWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.parent.run_jmetal_logic()
        self.finished.emit()

        