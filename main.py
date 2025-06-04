import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QComboBox, QProgressBar, QTextEdit, QFileDialog, QHBoxLayout, QFrame, QAction, QToolBar
)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from modules.settings_dialog import SettingsDialog
from modules.history_dialog import HistoryDialog
from modules.history_manager import save_history_entry

from modules.tts_engine import speak
from modules.recorder import record_until_silence
from modules.whisper_stt import transcribe
from modules.evaluator import evaluate_transcript
from modules.report_generator import generate_pdf_report

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'data', 'audio')

class RecorderThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path
        self.running = True
    def run(self):
        if self.running:
            result_path = record_until_silence(filename=self.audio_path)
            self.finished.emit(result_path)
    def stop(self):
        self.running = False
        self.terminate()

class InterviewApp(QMainWindow):
    


    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Mock Interview Simulator")
        self.setFixedSize(800, 690)
        self.setWindowIcon(QIcon('assets/app.png'))

        self.questions = []
        self.current_question = 0
        self.total_questions = 0
        self.transcript = ""
        self.interview_active = False
        self.latest_metrics = None
        self.recorder_thread = None
        self.question_count = 3
        self.dark_mode = False

        os.makedirs(AUDIO_DIR, exist_ok=True)

        self.init_ui()
        self.load_questions()
        self.apply_theme()

    def init_ui(self):
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        settings_action = QAction(QIcon('assets/setting.png'), 'Settings', self)
        settings_action.triggered.connect(self.open_settings_dialog)
        toolbar.addAction(settings_action)
        
        toolbar.addSeparator()  

        history_action = QAction(QIcon('assets/history.png'), 'History', self)
        history_action.triggered.connect(self.open_history_dialog)
        toolbar.addAction(history_action)


        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        header = QLabel("AI Mock Interview Simulator")
        header.setFont(QFont('Segoe UI', 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header)

        cat_frame = QFrame()
        cat_layout = QHBoxLayout(cat_frame)
        cat_label = QLabel("Interview Category:")
        cat_label.setFont(QFont('Segoe UI', 11))
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 11))
        self.category_combo.setFixedWidth(200)
        self.category_combo.addItems(["CSS", "Technical", "Business"])
        cat_layout.addWidget(cat_label)
        cat_layout.addWidget(self.category_combo)
        cat_layout.addStretch()
        self.main_layout.addWidget(cat_frame)

        self.start_btn = QPushButton("Start Interview")
        self.start_btn.setIcon(QIcon('assets/mic.png'))
        self.start_btn.clicked.connect(self.start_interview)
        self.main_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Interview")
        self.stop_btn.setIcon(QIcon('assets/stop.png'))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_interview)
        self.main_layout.addWidget(self.stop_btn)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.main_layout.addWidget(self.progress)

        self.status_label = QLabel("Status: Ready to begin")
        self.status_label.setFont(QFont('Segoe UI', 10))
        self.main_layout.addWidget(self.status_label)

        self.result_panel = QFrame()
        self.result_panel.hide()
        res_layout = QVBoxLayout(self.result_panel)
        self.overall_score = QLabel("")
        self.overall_score.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.overall_score.setAlignment(Qt.AlignCenter)
        res_layout.addWidget(self.overall_score)

        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setFont(QFont('Segoe UI', 10))
        res_layout.addWidget(self.feedback_text)

        btn_row = QHBoxLayout()
        self.save_report_btn = QPushButton("Download PDF Report")
        self.save_report_btn.setIcon(QIcon('assets/pdf.png'))
        self.save_report_btn.setEnabled(False)
        self.save_report_btn.clicked.connect(self.save_report)

        self.restart_btn = QPushButton("Restart Interview")
        self.restart_btn.setIcon(QIcon('assets/restart.png'))
        self.restart_btn.setEnabled(False)
        self.restart_btn.clicked.connect(self.restart_interview)

        btn_row.addWidget(self.save_report_btn)
        btn_row.addWidget(self.restart_btn)
        res_layout.addLayout(btn_row)

        self.main_layout.addWidget(self.result_panel)

        branding = QLabel("Powered by Muhammad Nabeel")
        branding.setFont(QFont("Segoe UI", 9, QFont.StyleItalic))
        branding.setStyleSheet("color: gray; margin-top: 10px;")
        branding.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(branding)

    def apply_theme(self):
     if self.dark_mode:
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3a3af0;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5757f7;
            }
            QComboBox {
                padding: 6px;
                border-radius: 4px;
                background-color: #2d2d3a;
                color: white;
                border: 1px solid #555;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d3a;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #28a745;
            }
            QTextEdit {
                background-color: #2d2d3a;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QFrame#resultPanel {
                background-color: #2a2a3a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 10px;
            }
            QToolButton {
                background-color: #3a3af0;
                border-radius: 4px;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #5757f7;
            }
        """)
     else:
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fb;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QComboBox {
                padding: 6px;
                border-radius: 4px;
                background-color: white;
                border: 1px solid #ccc;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                background-color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #28a745;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QFrame#resultPanel {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
            QToolButton {
                background-color: #007bff;
                border-radius: 4px;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #0056b3;
            }
        """)



    def load_questions(self):
        try:
            with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
        cat = self.category_combo.currentText()
        self.questions = data.get(cat, [])[:self.question_count]

        self.total_questions = len(self.questions)
        self.progress.setMaximum(self.total_questions)
        self.progress.setValue(0)

    def open_settings_dialog(self):
     dialog = SettingsDialog(self, current_question_count=self.question_count, dark_mode=self.dark_mode)
     if dialog.exec_():
        self.question_count, self.dark_mode = dialog.get_settings()
        self.apply_theme()

    def open_history_dialog(self):
     dialog = HistoryDialog(self)
     dialog.exec_()


    def start_interview(self):
        self.load_questions()
        if not self.questions:
            self.status_label.setText("No questions available.")
            return
        self.interview_active = True
        self.current_question = 0
        self.transcript = ""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.result_panel.hide()
        QTimer.singleShot(500, self.ask_next_question)

    def ask_next_question(self):
        if not self.interview_active:
            return
        if self.current_question < self.total_questions:
            question = self.questions[self.current_question]
            self.status_label.setText(f"Q{self.current_question+1}: {question}")
            speak(question)
            QTimer.singleShot(100, self.start_recording)
        else:
            self.finish_interview()

    def start_recording(self):
        audio_file = os.path.join(AUDIO_DIR, f"answer_{self.current_question+1}.wav")
        self.recorder_thread = RecorderThread(audio_file)
        self.recorder_thread.finished.connect(self.handle_recording_finished)
        self.recorder_thread.start()

    def handle_recording_finished(self, audio_file):
        if not self.interview_active:
            return
        text = transcribe(audio_file)
        if text.strip():
            self.transcript += text + " "
        self.current_question += 1
        self.progress.setValue(self.current_question)
        QTimer.singleShot(300, self.ask_next_question)

    def stop_interview(self):
        self.interview_active = False
        if self.recorder_thread and self.recorder_thread.isRunning():
            self.recorder_thread.stop()
        self.status_label.setText("Interview stopped early.")
        self.reset_ui()

    def finish_interview(self):
        self.interview_active = False
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Processing results...")
        results = evaluate_transcript(self.questions, self.transcript)
        self.latest_metrics = results
        save_history_entry(
    category=self.category_combo.currentText(),
    score=results['overall'],
    feedback=results['feedback']
)

        self.show_results(results)

    def show_results(self, results):
        self.overall_score.setText(f"Overall Score: {results['overall']}/10")
        self.feedback_text.setText(
            f"• Fluency: {results['fluency']}/10\n"
            f"• Vocabulary: {results['vocabulary']}/10\n"
            f"• Confidence: {results['confidence']}/10\n"
            f"• Structure: {results['structure']}/10\n"
            f"• Factual: {results['factual']}/10\n\n"
            f"Tips: {results['feedback']}"
        )
        self.result_panel.show()
        self.save_report_btn.setEnabled(True)
        self.restart_btn.setEnabled(True)
        self.status_label.setText("Interview complete. Results below.")

    def save_report(self):
        if not self.latest_metrics:
            return
        default_path = os.path.join("data", "reports", "Interview_Report.pdf")
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_path, "PDF Files (*.pdf)")
        if path:
            generate_pdf_report(
                path,
                category=self.category_combo.currentText(),
                results=self.latest_metrics,
                transcript=self.transcript
            )
            self.status_label.setText(f"Report saved to {path}")

    def restart_interview(self):
        self.reset_ui()

    def reset_ui(self):
        self.interview_active = False
        self.transcript = ""
        self.current_question = 0
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_report_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)
        self.result_panel.hide()
        self.progress.setValue(0)
        self.status_label.setText("Status: Ready to begin")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InterviewApp()
    window.show()
    sys.exit(app.exec_())
