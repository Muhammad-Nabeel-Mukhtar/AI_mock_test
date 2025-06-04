# modules/record_worker.py

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from modules.recorder import record_until_silence

class RecordWorker(QObject):
    finished = pyqtSignal(str)  # will emit the filename when done

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        result = record_until_silence(self.filename)
        self.finished.emit(result)
