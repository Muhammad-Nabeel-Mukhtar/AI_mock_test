from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QCheckBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_question_count=3, dark_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        # Question count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Number of Questions:"))
        self.question_spin = QSpinBox()
        self.question_spin.setRange(1, 30)  # ✅ Limit to 1–30
        self.question_spin.setValue(current_question_count)
        count_layout.addWidget(self.question_spin)
        layout.addLayout(count_layout)

        # Theme toggle
        self.theme_checkbox = QCheckBox("Enable Dark Theme")
        self.theme_checkbox.setChecked(dark_mode)
        layout.addWidget(self.theme_checkbox)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_settings(self):
        return self.question_spin.value(), self.theme_checkbox.isChecked()
