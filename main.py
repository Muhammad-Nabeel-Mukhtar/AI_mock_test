import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QComboBox, QProgressBar, QTextEdit, QFileDialog, QHBoxLayout, QFrame, QAction, QToolBar
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont

# Import modules
from modules.tts_engine import speak
from modules.recorder import record_until_silence
from modules.whisper_stt import transcribe
from modules.evaluator import evaluate_transcript

# Paths
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'data', 'audio')

class InterviewApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Mock Interview Simulator")
        self.setFixedSize(800, 650)
        self.setWindowIcon(QIcon('assets/app_icon.png'))

        self.questions = []
        self.current_question = 0
        self.total_questions = 0
        self.transcript = ""

        os.makedirs(AUDIO_DIR, exist_ok=True)

        self.init_ui()
        self.load_questions()

    def init_ui(self):
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        settings_action = QAction(QIcon('assets/settings.png'), 'Settings', self)
        toolbar.addAction(settings_action)
        history_action = QAction(QIcon('assets/history.png'), 'History', self)
        toolbar.addAction(history_action)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = QLabel("AI Mock Interview Simulator")
        header.setFont(QFont('Arial', 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        cat_frame = QFrame()
        cat_frame.setFrameShape(QFrame.StyledPanel)
        cat_layout = QHBoxLayout(cat_frame)
        cat_label = QLabel("Interview Category:")
        cat_label.setFont(QFont('Arial', 12))
        self.category_combo = QComboBox()
        self.category_combo.setFixedWidth(200)
        self.category_combo.addItems(["HR", "Technical", "Behavioral", "Mixed"])
        cat_layout.addWidget(cat_label)
        cat_layout.addWidget(self.category_combo)
        cat_layout.addStretch()
        main_layout.addWidget(cat_frame)

        self.start_btn = QPushButton("Start Interview")
        self.start_btn.setIcon(QIcon('assets/mic.png'))
        self.start_btn.setFont(QFont('Arial', 14))
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_interview)
        self.start_btn.setStyleSheet(
            "QPushButton{background-color:#0052cc;color:white;padding:12px;border-radius:6px;}"
            "QPushButton:hover{background-color:#0066ff;}"
        )
        main_layout.addWidget(self.start_btn)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(25)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(
            "QProgressBar{border:1px solid #ccc;border-radius:5px;text-align:center;}"
            "QProgressBar::chunk{background-color:#28a745;}"
        )
        main_layout.addWidget(self.progress)

        self.status_label = QLabel("Status: Ready to begin")
        self.status_label.setFont(QFont('Arial', 11))
        main_layout.addWidget(self.status_label)

        self.result_panel = QFrame()
        self.result_panel.setFrameShape(QFrame.StyledPanel)
        self.result_panel.hide()
        res_layout = QVBoxLayout(self.result_panel)
        self.overall_score = QLabel("")
        self.overall_score.setFont(QFont('Arial', 20, QFont.Bold))
        self.overall_score.setAlignment(Qt.AlignCenter)
        res_layout.addWidget(self.overall_score)
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setFont(QFont('Arial', 12))
        res_layout.addWidget(self.feedback_text)

        btn_row = QHBoxLayout()
        self.save_report_btn = QPushButton("Download PDF Report")
        self.save_report_btn.setIcon(QIcon('assets/pdf.png'))
        self.save_report_btn.setEnabled(False)
        self.save_report_btn.clicked.connect(self.save_report)
        self.email_report_btn = QPushButton("Send via Email")
        self.email_report_btn.setIcon(QIcon('assets/email.png'))
        self.email_report_btn.setEnabled(False)
        self.restart_btn = QPushButton("Restart Interview")
        self.restart_btn.setIcon(QIcon('assets/restart.png'))
        self.restart_btn.setEnabled(False)
        self.restart_btn.clicked.connect(self.restart_interview)
        btn_row.addWidget(self.save_report_btn)
        btn_row.addWidget(self.email_report_btn)
        btn_row.addWidget(self.restart_btn)
        res_layout.addLayout(btn_row)

        main_layout.addWidget(self.result_panel)
        self.setCentralWidget(central)

    def load_questions(self):
        try:
            with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {"questions": []}
        cat = self.category_combo.currentText()
        self.questions = data.get(cat, data.get("questions", []))
        self.total_questions = len(self.questions)

    def start_interview(self):
        self.load_questions()
        if not self.questions:
            self.status_label.setText("No questions available for this category.")
            return
        self.current_question = 0
        self.transcript = ""
        self.progress.setMaximum(self.total_questions)
        self.progress.setValue(0)
        self.status_label.setText("Interview in progress...")
        self.start_btn.setEnabled(False)
        self.result_panel.hide()
        QTimer.singleShot(500, self.ask_next_question)

    def ask_next_question(self):
        if self.current_question < self.total_questions:
            q = self.questions[self.current_question]
            self.status_label.setText(f"Question {self.current_question+1}/{self.total_questions}: {q}")
            speak(q)
            audio_file = os.path.join(AUDIO_DIR, f"answer_{self.current_question+1}.wav")
            record_until_silence(filename=audio_file)
            text = transcribe(audio_file)
            self.transcript += text + " "
            self.current_question += 1
            self.progress.setValue(self.current_question)
            QTimer.singleShot(500, self.ask_next_question)
        else:
            self.finish_interview()

    def finish_interview(self):
        self.status_label.setText("Interview complete. Processing results...")
        overall, feedback = evaluate_transcript(self.questions, self.transcript)
        self.show_results(overall, feedback)

    def show_results(self, overall_score, feedback):
        self.overall_score.setText(f"Overall Score: {overall_score}/10")
        self.feedback_text.setText(feedback)
        self.save_report_btn.setEnabled(True)
        self.email_report_btn.setEnabled(True)
        self.restart_btn.setEnabled(True)
        self.result_panel.show()
        self.status_label.setText("Interview complete. View your results below.")

    def save_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "Interview_Report.pdf", "PDF Files (*.pdf)")
        if path:
            self.status_label.setText(f"Report saved to {path}")

    def restart_interview(self):
        self.progress.setValue(0)
        self.start_btn.setEnabled(True)
        self.save_report_btn.setEnabled(False)
        self.email_report_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)
        self.status_label.setText("Status: Ready to begin")
        self.result_panel.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InterviewApp()
    window.show()
    sys.exit(app.exec_())


