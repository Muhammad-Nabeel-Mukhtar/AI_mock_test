from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLabel
from PyQt5.QtGui import QFont
from modules.history_manager import load_history

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interview History")
        self.setMinimumSize(500, 300)
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Your Past Interviews:")
        self.label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        self.load_history_entries()

    def load_history_entries(self):
        history = load_history()
        for entry in reversed(history):  # show latest first
            item = f"[{entry['timestamp']}] {entry['category']} - Score: {entry['score']}/10\n{entry['feedback']}"
            self.list_widget.addItem(item)
