import sys
import re
import csv
import os
import random
import string
import smtplib
import json
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QDateTimeEdit, QStackedWidget, QFormLayout, QDialog, QInputDialog,
    QSplashScreen, QFrame, QProgressBar, QScrollArea, QSpinBox, QSystemTrayIcon, QMenu, QAction,QGroupBox
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QDate, QTime, QSize, QPoint, QUrl, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage, QColor, QPainter, QPainterPath, QPen, QFontDatabase
from PyQt5.QtMultimedia import QSoundEffect
import csv
from lastwelcomme import Ui_Form as WelcomeUI
from lastloog import Ui_Form as LoginUI
from lastregggg import Ui_Form as RegisterUI
from collections import deque
from cryptography.fernet import Fernet

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "cybersystem100@gmail.com"
EMAIL_PASSWORD = "eibihmhuuqqhvrdi"
VERIFICATION_EXPIRE_MINUTES = 2


class AIAssistant:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.responses = self.load_responses()
        
    def load_responses(self):
        try:
            responses_path = os.path.join(os.path.dirname(__file__), "ai_responses.json")
            if os.path.exists(responses_path):
                with open(responses_path, "r", encoding='utf-8') as file:
                    data = json.load(file)
                    required_keys = [
                        "greetings", "task_help", "pomodoro", "streak", "unknown",
                        "name_response", "student_specific", "motivation", "study_tips",
                        "task_count", "task_classification"
                    ]
                    if not all(key in data for key in required_keys):
                        raise ValueError("Missing required response categories in JSON")
                    return data
            raise FileNotFoundError("AI responses file not found")
        except Exception as e:
            print(f"Failed to load AI responses: {str(e)}")
            return {
                "greetings": ["⚠️ Error - Default Response"],
                "task_help": ["❌ Couldn't load tasks - Default"],
                "pomodoro": ["⏱️ Pomodoro error - Default"],
                "streak": ["🔥 Streak data unavailable"],
                "unknown": ["🤖 I'm having trouble understanding"],
                "name_response": ["AI Error - Default Response"],
                "student_specific": ["AI Error - Default Response"],
                "motivation": ["AI Error - Default Response"],
                "study_tips": ["AI Error - Default Response"],
                "task_count": ["❌ Task count unavailable - Default"],
                "task_classification": ["❌ Task classification unavailable - Default"]
            }

    def _get_time_data(self):
        """Get current time and date data"""
        tz = pytz.timezone("Europe/Bucharest")
        now = datetime.now(tz)
        return {
            "current_date": now.strftime("%B %d, %Y"),
            "current_time": now.strftime("%H:%M"),
            "pomodoro_emoji": "⏳" if now.hour < 12 else "🌙"
        }
      
    def _get_tomorrow_tasks(self):
        """Get tasks due tomorrow with improved handling"""
        tz = pytz.timezone("Europe/Bucharest")
        tomorrow = datetime.now(tz).date() + timedelta(days=1)
        tomorrow_tasks = []
        
        for task in self.task_manager.tasks:
            try:
                due_date = getattr(task, 'due_date', None)
                if not due_date:
                    continue
                    
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                
                if due_date == tomorrow:
                    tomorrow_tasks.append(task)
                    
            except Exception as e:
                print(f"Error processing task due date: {e}")
                continue
                
        return tomorrow_tasks
    
    def _get_task_status_counts(self):
        
        counts = {
        "Pending": 0,
        "Completed": 0,
        "Uncompleted": 0,
        "Overdue": 0
    }
       
        tz = pytz.timezone("Europe/Bucharest")
        today = datetime.now(tz).date()
        
        for task in self.task_manager.tasks:
            try:
                # Handle task status
                if getattr(task, 'completed', False):
                    counts["Completed"] += 1
                else:
                    counts["Uncompleted"] += 1
                
                # Handle due dates
                due_date = getattr(task, 'due_date', None)
                if due_date:
                    if isinstance(due_date, str):
                        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                    
                    if due_date < today and not getattr(task, 'completed', False):
                        counts["Overdue"] += 1
                    elif not getattr(task, 'completed', False):
                        counts["Pending"] += 1
                        
            except Exception as e:
                print(f"Error processing task: {e}")
                continue
        
        return counts
    
    
    def format_response(self, message):
        """Format the response with beautiful styling"""
        FIXED_WIDTH = 60
        border = "═" * (FIXED_WIDTH - 2)
        header = f"╔{border}╗"
        footer = f"╚{border}╝"
        
        formatted_msg = f"\n{header}\n"
        for line in message.split('\n'):
            centered_line = line.center(50)
            formatted_msg += f"{centered_line}\n"
        formatted_msg += f"{footer}\n"
        return formatted_msg
    
    def get_response(self, user_input):
        """Enhanced response handler with smarter matching"""
        lower_input = user_input.lower()
        
        # Check for Apollo's name (with more variations)
        if any(word in lower_input for word in ["your name", "who are you", "what's your name", "apollo", "who made you"]):
            if "who made you" in lower_input or "who develop" in lower_input:
                return self.format_response(random.choice(self.responses["DevelopApollo"]))
            return self.format_response(random.choice(self.responses["name_response"]))
        
        # Check for gratitude
        if any(word in lower_input for word in ["thanks", "thank you", "thx", "appreciate"]):
            return self.format_response(random.choice(self.responses["gratitude"]))
        
        if any(word in lower_input for word in ["how are you", "how r u", "how's it going", "how are u", "how do you feel", "what's up", "sup", "how you doing", "how you doin", "how are things", "you good"]):
            return self.format_response(random.choice(self.responses["how_are_you"]))
        
        # Check for doctor mention
        if any(word in lower_input for word in ["best doctor", "doctor", "tamer", "abdelatif"]):
            return self.format_response(random.choice(self.responses["Doctor_tip"]))
        
        # Handle time queries
        if any(word in lower_input for word in ["time", "what time is it", "current time", "date", "current date"]):
            time_data = self._get_time_data()
            response = random.choice(self.responses["time_query"]).format(**time_data)
            return self.format_response(response)
        
        # Handle task-related queries with improved matching
        task_related_words = ["tasks", "todo", "assignment", "homework", "projects", "work"]
        if any(word in lower_input for word in task_related_words):
            # Check for specific task queries
            if "how many" in lower_input or "count" in lower_input:
                total_tasks = len(self.task_manager.tasks)
                task_word = "task" if total_tasks == 1 else "tasks"
                response = random.choice(self.responses["task_count"]).format(
                    total_tasks=total_tasks,
                    task_word=task_word
                )
                return self.format_response(response)
            
            if "classify" in lower_input or "breakdown" in lower_input or "status" in lower_input:
                status_counts = self._get_task_status_counts()
                response = random.choice(self.responses["task_classification"]).format(
                    pending_count=status_counts["Pending"],
                    completed_count=status_counts["Completed"],
                    uncompleted_count=status_counts["Uncompleted"],
                    overdue_count=status_counts["Overdue"]
                )
                return self.format_response(response)
            
            return self.format_response(random.choice(self.responses["task_help"]))
        
        # Handle Pomodoro queries
        if any(word in lower_input for word in ["pomodoro", "timer", "focus session", "study timer"]):
            return self.format_response(random.choice(self.responses["pomodoro"]))
        
        # Handle streak queries
        if "streak" in lower_input or "chain" in lower_input:
            streak = self.task_manager.task_history.calculate_streak()
            response = random.choice(self.responses["streak"]).format(streak_days=streak)
            return self.format_response(response)
        
        # Handle study-related queries
        if any(word in lower_input for word in ["study", "exam", "learn", "revise", "revision"]):
            if "tip" in lower_input or "advice" in lower_input:
                return self.format_response(random.choice(self.responses["study_tips"]))
            return self.format_response(random.choice(self.responses["student_specific"]))
        
        # Handle motivation queries
        if any(word in lower_input for word in ["motivate", "encourage", "tired", "burnout", "lazy"]):
            return self.format_response(random.choice(self.responses["motivation"]))
        
        # Handle deadline queries
        if any(word in lower_input for word in ["deadline", "due date", "when is", "due soon"]):
            next_task = self.task_manager.get_most_urgent_task()
            if next_task:
                response = random.choice(self.responses["pattern_deadline"]).format(
                    task_name=next_task.title,
                    deadline_date=next_task.due_date,
                    class_name=next_task.category,
                    time_remaining=self._get_time_remaining(next_task.due_date)
                )
                return self.format_response(response)
            return self.format_response("You have no upcoming deadlines! Great job staying on top of things! 🎉")
        
        # Handle tomorrow queries
        if "tomorrow" in lower_input or "due tomorrow" in lower_input:
            tz = pytz.timezone("Europe/Bucharest")
            tomorrow = datetime.now(tz).date() + timedelta(days=1)
            tomorrow_date = tomorrow.strftime("%B %d, %Y")
            
            tomorrow_tasks = self._get_tomorrow_tasks()
            
            if not tomorrow_tasks:
                response = random.choice(self.responses["tomorrow_no_tasks"])
                return self.format_response(response.format(tomorrow_date=tomorrow_date))
            
            # Calculate dynamic data
            tomorrow_tasks_count = len(tomorrow_tasks)
            urgent_count = sum(1 for task in tomorrow_tasks if getattr(task, "urgent", False))
            upcoming_tasks = ", ".join(task.title for task in tomorrow_tasks if hasattr(task, "title")) or "None"
            tomorrow_events = upcoming_tasks
            
            # Select and format response
            response = random.choice(self.responses["tomorrow_query"])
            return self.format_response(response.format(
                tomorrow_date=tomorrow_date,
                upcoming_tasks=upcoming_tasks,
                tomorrow_tasks_count=tomorrow_tasks_count,
                urgent_count=urgent_count,
                tomorrow_events=tomorrow_events
            ))
        
        # Handle help queries
        if "help" in lower_input or "what can you do" in lower_input:
            return self.format_response(random.choice(self.responses["pattern_help"]))
        
        # Handle user guide queries
        if "userguide" in lower_input or "user guide" in lower_input or "how to use" in lower_input:
            return self.format_response(random.choice(self.responses["userGuide"]))
        
        # Handle greetings
        if any(word in lower_input for word in ["hello", "hi", "hey", "greetings", "welcome", "sup"]):
            return self.format_response(random.choice(self.responses["greetings"]))
        
        # Handle student-specific queries
        if any(word in lower_input for word in ["student", "college", "university", "school", "course", "class"]):
            return self.format_response(random.choice(self.responses["student_specific"]))
        
        # Handle creator queries
        if any(word in lower_input for word in ["who made you", "who created you", "who developed you", "your creator"]):
            return self.format_response(random.choice(self.responses["DevelopApollo"]))
        
        # Handle completed tasks queries
        if any(word in lower_input for word in ["completed", "finished", "done"]):
            completed_count = self.task_manager.get_completed_count()
            response = random.choice(self.responses["pattern_completed"]).format(
                completed_count=completed_count,
                motivational_phrase=random.choice(self.responses["motivation"])
            )
            return self.format_response(response)
        
        # Default response for unknown queries
        return self.format_response(random.choice(self.responses["unknown"]))
    
    def _get_time_remaining(self, due_date):
        """Calculate time remaining until due date"""
        try:
            tz = pytz.timezone("Europe/Bucharest")
            today = datetime.now(tz).date()
            
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            
            delta = due_date - today
            
            if delta.days == 0:
                return "today"
            elif delta.days == 1:
                return "1 day"
            elif delta.days < 7:
                return f"{delta.days} days"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''}"
            else:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''}"
        except:
            return "soon"

class CircularWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.diameter = 450
        self.setFixedSize(self.diameter, self.diameter)
        self.old_pos = None
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)

        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 40, QFont.Bold))

        self.session_label = QLabel("Work Time")
        self.session_label.setAlignment(Qt.AlignCenter)
        self.session_label.setFont(QFont("Segoe UI", 16))

        self.counter_label = QLabel("Sessions: 0/4")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setFont(QFont("Segoe UI", 12))

        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.toggle_timer)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.reset_button)

        settings_layout = QVBoxLayout()

        self.work_spin, work_layout = self.create_custom_spinbox("Work (min):", 25, 1, 60)
        self.short_break_spin, short_layout = self.create_custom_spinbox("Short Break:", 5, 1, 30)
        self.long_break_spin, long_layout = self.create_custom_spinbox("Long Break:", 15, 5, 60)
        self.sessions_spin, session_layout = self.create_custom_spinbox("Sessions:", 4, 1, 10)

        settings_layout.addLayout(work_layout)
        settings_layout.addLayout(short_layout)
        settings_layout.addLayout(long_layout)
        settings_layout.addLayout(session_layout)

        settings_layout.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.session_label)
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.counter_label)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(settings_layout)

    def create_custom_spinbox(self, label_text, default, min_val, max_val):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setButtonSymbols(QSpinBox.NoButtons)
        spin.valueChanged.connect(self.update_settings)

        plus = QPushButton("+")
        plus.setFixedSize(30, 30)
        plus.setStyleSheet("""
            QPushButton {
                background-color: #98FFCC;
                color: #2E2E2E;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7BE6B0;
            }
            QPushButton:pressed {
                background-color: #5FCC94;
            }
        """)
        plus.clicked.connect(lambda: spin.setValue(spin.value() + 1))

        minus = QPushButton("–")
        minus.setFixedSize(30, 30)
        minus.setStyleSheet("""
            QPushButton {
                background-color: #FF9898;
                color: #2E2E2E;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E67B7B;
            }
            QPushButton:pressed {
                background-color: #CC5F5F;
            }
        """)
        minus.clicked.connect(lambda: spin.setValue(spin.value() - 1))

        layout.addWidget(label)
        layout.addWidget(minus)
        layout.addWidget(spin)
        layout.addWidget(plus)
        return spin, layout

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self.diameter, self.diameter)
        painter.fillPath(path, QColor("#FFFFFF"))
        painter.setPen(QPen(QColor("#98FFCC"), 3))
        painter.drawEllipse(0, 0, self.diameter, self.diameter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.pos() - self.old_pos)
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class PomodoroApp(CircularWindow):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        self.work_time = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 15 * 60
        self.pomodoros_before_long_break = 4
        self.current_pomodoros = 0
        self.is_working = True
        self.is_active = False
        self.time_left = self.work_time

        self.setWindowTitle("Pomodoro Timer")
        self.setup_styles()
        self.setup_tray_icon()
        self.load_settings()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def setup_styles(self):
        self.setStyleSheet("""
            QLabel {
                color: #2E2E2E;
            }
            QPushButton {
                background-color: #98FFCC;
                color: #2E2E2E;
                border: none;
                padding: 6px 12px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7BE6B0;
            }
            QPushButton:pressed {
                background-color: #5FCC94;
            }
            QSpinBox {
                padding: 5px;
                font-size: 14px;
                background-color: #F0F0F0;
                color: #2E2E2E;
                border-radius: 8px;
                min-height: 30px;
                max-width: 60px;
                text-align: center;
            }
        """)


    def setup_tray_icon(self):
    # First create the tray icon
     self.tray_icon = QSystemTrayIcon(self)
 
     self.tray_icon.setIcon(QIcon.fromTheme("timer"))
    
    # Configure the rest
     self.tray_icon.setToolTip("Pomodoro Timer")
    
     tray_menu = QMenu()
     show_action = QAction("Show", self)
     show_action.triggered.connect(self.showNormal)
     quit_action = QAction("Quit", self)
     quit_action.triggered.connect(QApplication.quit)
    
     tray_menu.addAction(show_action)
     tray_menu.addAction(quit_action)
     self.tray_icon.setContextMenu(tray_menu)
     self.tray_icon.activated.connect(self.tray_icon_clicked)
     self.tray_icon.show()

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()

    def toggle_timer(self):
        if self.is_active:
            self.timer.stop()
            self.start_button.setText("Start")
            self.is_active = False
        else:
            self.timer.start(1000)
            self.start_button.setText("Pause")
            self.is_active = True
            self.animate_button(self.start_button)

    def reset_timer(self):
        self.timer.stop()
        self.is_active = False
        self.is_working = True
        self.current_pomodoros = 0
        self.time_left = self.work_time
        self.session_label.setText("Work Time")
        self.update_display()
        self.start_button.setText("Start")

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            if self.is_working:
                self.current_pomodoros += 1
                if self.task_manager.tasks:
                    highest_task = max(self.task_manager.tasks)
                    self.task_manager.mark_task(highest_task.title, "Completed")
                    main_window = self.parent()
                    while main_window and not isinstance(main_window, MainWindow):
                        main_window = main_window.parent()
                    if main_window:
                        main_window.update_task_list()
                        main_window.update_history_list()
                        main_window.streak_page.update_streak()
                if self.current_pomodoros % self.pomodoros_before_long_break == 0:
                    self.time_left = self.long_break
                    self.session_label.setText("Long Break")
                    self.show_notification("Long Break", "Time for a longer rest!")
                else:
                    self.time_left = self.short_break
                    self.session_label.setText("Short Break")
                    self.show_notification("Short Break", "Take a quick rest!")
            else:
                self.time_left = self.work_time
                self.session_label.setText("Work Time")
                self.show_notification("Work Time", "Back to work!")
            self.is_working = not self.is_working
        self.update_display()


    def update_display(self):
        self.time_label.setText(self.format_time(self.time_left))
        self.counter_label.setText(f"Sessions: {self.current_pomodoros}/{self.pomodoros_before_long_break}")
        self.save_settings()

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def update_settings(self):
        self.work_time = self.work_spin.value() * 60
        self.short_break = self.short_break_spin.value() * 60
        self.long_break = self.long_break_spin.value() * 60
        self.pomodoros_before_long_break = self.sessions_spin.value()
        if self.is_working and not self.is_active:
            self.time_left = self.work_time
        self.update_display()

    def show_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)

    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        original_geometry = button.geometry()
        animation.setStartValue(original_geometry)
        animation.setEndValue(original_geometry.adjusted(0, 0, 0, 0))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def load_settings(self):
        settings_path = os.path.join(os.path.dirname(__file__), "pomodoro_settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as file:
                    settings = json.load(file)
                    self.work_spin.setValue(settings.get("work", 25))
                    self.short_break_spin.setValue(settings.get("short_break", 5))
                    self.long_break_spin.setValue(settings.get("long_break", 15))
                    self.sessions_spin.setValue(settings.get("sessions", 4))
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        settings = {
            "work": self.work_spin.value(),
            "short_break": self.short_break_spin.value(),
            "long_break": self.long_break_spin.value(),
            "sessions": self.sessions_spin.value()
        }
        settings_path = os.path.join(os.path.dirname(__file__), "pomodoro_settings.json")
        try:
            with open(settings_path, "w") as file:
                json.dump(settings, file)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Confirm Exit", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()

class QuizPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.question_times = []  # To track time spent on each question
        self.current_question_start_time = None
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Timer display
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")
        layout.addWidget(self.timer_label)

        # Quiz progress label
        self.progress_label = QLabel("Question 0/0")
        self.progress_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 20)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Question display
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.question_label)

        # Options layout
        self.option_buttons = []
        for i in range(4):
            btn = QPushButton()
            btn.setStyleSheet("""
                text-align: left; 
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
            btn.clicked.connect(lambda _, idx=i: self.check_answer(idx))
            self.option_buttons.append(btn)
            layout.addWidget(btn)

        # Explanation label
        self.explanation_label = QLabel()
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("""
            font-size: 13px;
            color: #666;
            font-style: italic;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        self.explanation_label.hide()
        layout.addWidget(self.explanation_label)

        # Score display
        self.score_label = QLabel("Score: 0/0")
        self.score_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.score_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_question)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_question)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def setup_timer(self):
        self.quiz_timer = QTimer(self)
        self.quiz_timer.timeout.connect(self.update_timer)
        self.reset_timer()

    def reset_timer(self):
        self.quiz_timer.stop()  # Ensure timer is stopped before resetting
        self.time_left = QTime(0, 25, 0)  # 25 minutes
        self.timer_label.setText(self.time_left.toString("mm:ss"))
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")

    def start_timer(self):
        self.reset_timer()
        self.quiz_timer.start(1000)  # Update every second

    def update_timer(self):
        self.time_left = self.time_left.addSecs(-1)
        self.timer_label.setText(self.time_left.toString("mm:ss"))
        
        # Change color when time is running out
        if self.time_left <= QTime(0, 1, 0):
            self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff0000;")
        
        # Time's up!
        if self.time_left == QTime(0, 0, 0):
            self.quiz_timer.stop()
            self.show_results(forced=True)

    def load_questions(self, questions):
        # Reset all quiz state when loading new questions
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.question_times = [0] * len(questions)
        self.current_question_start_time = None
        self.start_timer()  # This will properly reset the timer
        self.update_question()

    def update_question(self):
        if not self.questions:
            self.question_label.setText("No questions available.")
            return

        # Record time spent on previous question
        if self.current_question_start_time is not None:
            time_spent = self.current_question_start_time.elapsed() / 1000  # in seconds
            self.question_times[self.current_question] = time_spent

        question_data = self.questions[self.current_question]
        self.question_label.setText(question_data["question"])

        # Reset all buttons to default state first
        for i, btn in enumerate(self.option_buttons):
            btn.setStyleSheet("""
                text-align: left; 
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
            btn.setEnabled(True)

        # Set button texts and styles based on current state
        correct_answer = question_data.get("answer", "")
        user_answer_idx = question_data.get("user_answer", -1)
        is_answered = question_data.get("answered", False)

        for i, option in enumerate(question_data["options"]):
            self.option_buttons[i].setText(option)
            
            if is_answered:
                if option.startswith(correct_answer + ")"):
                    self.option_buttons[i].setStyleSheet("""
                        background-color: #5cb85c; 
                        color: white;
                        border: 1px solid #4cae4c;
                        border-radius: 4px;
                    """)
                elif i == user_answer_idx:
                    self.option_buttons[i].setStyleSheet("""
                        background-color: #d9534f; 
                        color: white;
                        border: 1px solid #d43f3a;
                        border-radius: 4px;
                    """)
                else:
                    self.option_buttons[i].setStyleSheet("""
                        text-align: left; 
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        color: #999;
                    """)
                self.option_buttons[i].setEnabled(False)

        self.progress_label.setText(f"Question {self.current_question + 1}/{len(self.questions)}")
        self.progress_bar.setValue(self.current_question + 1)
        self.progress_bar.setMaximum(len(self.questions))
        self.score_label.setText(f"Score: {self.score}/{len(self.questions)}")

        self.prev_btn.setEnabled(self.current_question > 0)
        
        # Show/hide explanation based on whether question was answered
        if is_answered and "explanation" in question_data:
            self.explanation_label.setText(f"Explanation: {question_data['explanation']}")
            self.explanation_label.show()
        else:
            self.explanation_label.hide()
        
        # Always enable Next/Finish button (changed from original)
        if self.current_question == len(self.questions) - 1:
            self.next_btn.setText("Finish")
            self.next_btn.setEnabled(True)  # Always enable Finish button
        else:
            self.next_btn.setText("Next")
            self.next_btn.setEnabled(True)  # Always enable Next button

        # Reset question start time
        self.current_question_start_time = QTime.currentTime()
        self.current_question_start_time.start()

    def check_answer(self, option_idx):
        if self.questions[self.current_question].get("answered", False):
            return  # Don't allow re-answering

        question_data = self.questions[self.current_question]
        correct_answer = question_data["answer"]
        selected_option = question_data["options"][option_idx]
        is_correct = selected_option.startswith(correct_answer + ")")

        # Mark question as answered
        self.questions[self.current_question]["answered"] = True
        self.questions[self.current_question]["user_answer"] = option_idx
        self.questions[self.current_question]["is_correct"] = is_correct

        # Update score if this is the first time answering
        if is_correct:
            self.score += 1

        # Update button colors and disable them
        for i, btn in enumerate(self.option_buttons):
            option = question_data["options"][i]
            if option.startswith(correct_answer + ")"):
                btn.setStyleSheet("""
                    background-color: #5cb85c; 
                    color: white;
                    border: 1px solid #4cae4c;
                    border-radius: 4px;
                """)
            elif i == option_idx and not is_correct:
                btn.setStyleSheet("""
                    background-color: #d9534f; 
                    color: white;
                    border: 1px solid #d43f3a;
                    border-radius: 4px;
                """)
            else:
                btn.setStyleSheet("""
                    text-align: left; 
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    color: #999;
                """)
            btn.setEnabled(False)

        # Show explanation if available
        if "explanation" in question_data:
            self.explanation_label.setText(f"Explanation: {question_data['explanation']}")
            self.explanation_label.show()

        self.score_label.setText(f"Score: {self.score}/{len(self.questions)}")
        
        # Enable Finish button if this was the last question
        if self.current_question == len(self.questions) - 1:
            self.next_btn.setEnabled(True)

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_question()
        else:
            self.show_results()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question()

    def show_results(self, forced=False):
        # Record time for current question
        if self.current_question_start_time is not None:
            time_spent = self.current_question_start_time.elapsed() / 1000
            self.question_times[self.current_question] = time_spent

        # Stop the timer
        self.quiz_timer.stop()

        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Quiz Results")
        result_dialog.setModal(True)
        result_dialog.resize(600, 500)

        layout = QVBoxLayout()

        # Header with score and time info
        header = QLabel()
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        if forced:
            header.setText("Time's up! Here are your results:")
        else:
            header.setText("Quiz completed! Here are your results:")
        
        layout.addWidget(header)

        # Score and time summary
        total_time = sum(self.question_times)
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        summary = QLabel(f"""
            <p><b>Final Score:</b> {self.score}/{len(self.questions)}</p>
            <p><b>Total Time:</b> {minutes}m {seconds}s</p>
            <p><b>Average Time per Question:</b> {total_time/len(self.questions):.1f}s</p>
        """)
        layout.addWidget(summary)

        # Motivational message
        percentage = (self.score / len(self.questions)) * 100
        if percentage >= 80:
            motivation = "Excellent work! You've mastered this material."
        elif percentage >= 60:
            motivation = "Good job! You're on the right track."
        else:
            motivation = "Keep practicing! You'll improve with more study."
        
        motivation_label = QLabel(motivation)
        motivation_label.setStyleSheet("font-size: 16px; color: #5bc0de;")
        layout.addWidget(motivation_label)

        # Detailed results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        for i, question in enumerate(self.questions):
            question_box = QVBoxLayout()
            question_box.setContentsMargins(10, 10, 10, 10)
            question_box.setSpacing(5)

            # Question header with time spent
            time_spent = self.question_times[i]
            question_header = QLabel(f"Question {i+1} (Time: {time_spent:.1f}s)")
            question_header.setStyleSheet("font-weight: bold;")
            question_box.addWidget(question_header)

            # Question text
            question_label = QLabel(question['question'])
            question_label.setWordWrap(True)
            question_box.addWidget(question_label)

            # User's answer and correctness
            user_answer_idx = question.get("user_answer", -1)
            if user_answer_idx == -1:
                answer_status = QLabel("Not answered")
                answer_status.setStyleSheet("color: #f0ad4e;")
            else:
                if question["is_correct"]:
                    answer_status = QLabel("Correct!")
                    answer_status.setStyleSheet("color: #5cb85c;")
                else:
                    answer_status = QLabel("Incorrect")
                    answer_status.setStyleSheet("color: #d9534f;")
            question_box.addWidget(answer_status)

            # Options with highlighting
            correct_answer = question["answer"]
            for j, option in enumerate(question["options"]):
                option_label = QLabel(option)
                if option.startswith(correct_answer + ")"):
                    option_label.setStyleSheet("color: #5cb85c; font-weight: bold;")
                elif j == user_answer_idx:
                    option_label.setStyleSheet("color: #d9534f;")
                question_box.addWidget(option_label)

            # Explanation if available
            if "explanation" in question:
                explanation_label = QLabel(f"Explanation: {question['explanation']}")
                explanation_label.setWordWrap(True)
                explanation_label.setStyleSheet("font-style: italic; color: #777;")
                question_box.addWidget(explanation_label)

            content_layout.addLayout(question_box)
            content_layout.addWidget(QLabel(""))  # Add space between questions

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(result_dialog.accept)
        layout.addWidget(close_btn)

        result_dialog.setLayout(layout)
        result_dialog.exec_()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.question_times = []
        self.current_question_start_time = None
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Timer display
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")
        layout.addWidget(self.timer_label)

        # Quiz progress label
        self.progress_label = QLabel("Question 0/0")
        self.progress_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 20)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Question display
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.question_label)

        # Options layout
        self.option_buttons = []
        for i in range(4):
            btn = QPushButton()
            btn.setStyleSheet("""
                text-align: left; 
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
            btn.clicked.connect(lambda _, idx=i: self.check_answer(idx))
            self.option_buttons.append(btn)
            layout.addWidget(btn)

        # Explanation label
        self.explanation_label = QLabel()
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("""
            font-size: 13px;
            color: #666;
            font-style: italic;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        self.explanation_label.hide()
        layout.addWidget(self.explanation_label)

        # Score display
        self.score_label = QLabel("Score: 0/0")
        self.score_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.score_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_question)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_question)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def setup_timer(self):
        self.quiz_timer = QTimer(self)
        self.quiz_timer.timeout.connect(self.update_timer)
        self.reset_timer()

    def reset_timer(self):
        self.quiz_timer.stop()  # Stop timer if running
        self.time_left = QTime(0, 25, 0)  # 25 minutes
        self.timer_label.setText(self.time_left.toString("mm:ss"))
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")
        
    def start_timer(self):
        self.reset_timer()  # This now properly resets the timer
        self.quiz_timer.start(1000)  # Update every second

    def update_timer(self):
        self.time_left = self.time_left.addSecs(-1)
        self.timer_label.setText(self.time_left.toString("mm:ss"))
        
        # Change color when time is running out
        if self.time_left <= QTime(0, 1, 0):
            self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff0000;")
        
        # Time's up!
        if self.time_left == QTime(0, 0, 0):
            self.quiz_timer.stop()
            self.show_results(forced=True)

    def load_questions(self, questions):
        # Reset everything when loading new questions
        self.questions = questions
        self.current_question = 0
        self.score = 0
        self.question_times = [0] * len(questions)
        self.current_question_start_time = None
        self.start_timer()  # This will properly reset the timer
        self.update_question()

    def update_question(self):
        if not self.questions:
            self.question_label.setText("No questions available.")
            return

        # Record time spent on previous question
        if self.current_question_start_time is not None:
            time_spent = self.current_question_start_time.elapsed() / 1000  # in seconds
            self.question_times[self.current_question] = time_spent

        question_data = self.questions[self.current_question]
        self.question_label.setText(question_data["question"])

        # Reset all buttons to default state first
        for i, btn in enumerate(self.option_buttons):
            btn.setStyleSheet("""
                text-align: left; 
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            """)
            btn.setEnabled(True)

        # Set button texts and styles based on current state
        correct_answer = question_data.get("answer", "")
        user_answer_idx = question_data.get("user_answer", -1)
        is_answered = question_data.get("answered", False)

        for i, option in enumerate(question_data["options"]):
            self.option_buttons[i].setText(option)
            
            if is_answered:
                if option.startswith(correct_answer + ")"):
                    self.option_buttons[i].setStyleSheet("""
                        background-color: #5cb85c; 
                        color: white;
                        border: 1px solid #4cae4c;
                        border-radius: 4px;
                    """)
                elif i == user_answer_idx:
                    self.option_buttons[i].setStyleSheet("""
                        background-color: #d9534f; 
                        color: white;
                        border: 1px solid #d43f3a;
                        border-radius: 4px;
                    """)
                else:
                    self.option_buttons[i].setStyleSheet("""
                        text-align: left; 
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        color: #999;
                    """)
                self.option_buttons[i].setEnabled(False)

        self.progress_label.setText(f"Question {self.current_question + 1}/{len(self.questions)}")
        self.progress_bar.setValue(self.current_question + 1)
        self.progress_bar.setMaximum(len(self.questions))
        self.score_label.setText(f"Score: {self.score}/{len(self.questions)}")

        self.prev_btn.setEnabled(self.current_question > 0)
        
        # Show/hide explanation based on whether question was answered
        if is_answered and "explanation" in question_data:
            self.explanation_label.setText(f"Explanation: {question_data['explanation']}")
            self.explanation_label.show()
        else:
            self.explanation_label.hide()
        
        # Enable Next button always except for last question (which becomes Finish)
        if self.current_question == len(self.questions) - 1:
            self.next_btn.setText("Finish")
            self.next_btn.setEnabled(is_answered)  # Only enable Finish if answered
        else:
            self.next_btn.setText("Next")
            self.next_btn.setEnabled(True)  # Always enable Next button

        # Reset question start time
        self.current_question_start_time = QTime.currentTime()
        self.current_question_start_time.start()

    def check_answer(self, option_idx):
        if self.questions[self.current_question].get("answered", False):
            return  # Don't allow re-answering

        question_data = self.questions[self.current_question]
        correct_answer = question_data["answer"]
        selected_option = question_data["options"][option_idx]
        is_correct = selected_option.startswith(correct_answer + ")")

        # Mark question as answered
        self.questions[self.current_question]["answered"] = True
        self.questions[self.current_question]["user_answer"] = option_idx
        self.questions[self.current_question]["is_correct"] = is_correct

        # Update score if this is the first time answering
        if is_correct:
            self.score += 1

        # Update button colors and disable them
        for i, btn in enumerate(self.option_buttons):
            option = question_data["options"][i]
            if option.startswith(correct_answer + ")"):
                btn.setStyleSheet("""
                    background-color: #5cb85c; 
                    color: white;
                    border: 1px solid #4cae4c;
                    border-radius: 4px;
                """)
            elif i == option_idx and not is_correct:
                btn.setStyleSheet("""
                    background-color: #d9534f; 
                    color: white;
                    border: 1px solid #d43f3a;
                    border-radius: 4px;
                """)
            else:
                btn.setStyleSheet("""
                    text-align: left; 
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    color: #999;
                """)
            btn.setEnabled(False)

        # Show explanation if available
        if "explanation" in question_data:
            self.explanation_label.setText(f"Explanation: {question_data['explanation']}")
            self.explanation_label.show()

        self.score_label.setText(f"Score: {self.score}/{len(self.questions)}")
        
        # Enable Finish button if this was the last question
        if self.current_question == len(self.questions) - 1:
            self.next_btn.setEnabled(True)

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.update_question()
        else:
            self.show_results()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question()

    def show_results(self, forced=False):
        # Record time for current question
        if self.current_question_start_time is not None:
            time_spent = self.current_question_start_time.elapsed() / 1000
            self.question_times[self.current_question] = time_spent

        # Stop the timer
        self.quiz_timer.stop()

        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Quiz Results")
        result_dialog.setModal(True)
        result_dialog.resize(600, 500)

        layout = QVBoxLayout()

        # Header with score and time info
        header = QLabel()
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        if forced:
            header.setText("Time's up! Here are your results:")
        else:
            header.setText("Quiz completed! Here are your results:")
        
        layout.addWidget(header)

        # Score and time summary
        total_time = sum(self.question_times)
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        summary = QLabel(f"""
            <p><b>Final Score:</b> {self.score}/{len(self.questions)}</p>
            <p><b>Total Time:</b> {minutes}m {seconds}s</p>
            <p><b>Average Time per Question:</b> {total_time/len(self.questions):.1f}s</p>
        """)
        layout.addWidget(summary)

        # Motivational message
        percentage = (self.score / len(self.questions)) * 100
        if percentage >= 80:
            motivation = "Excellent work! You've mastered this material."
        elif percentage >= 60:
            motivation = "Good job! You're on the right track."
        else:
            motivation = "Keep practicing! You'll improve with more study."
        
        motivation_label = QLabel(motivation)
        motivation_label.setStyleSheet("font-size: 16px; color: #5bc0de;")
        layout.addWidget(motivation_label)

        # Detailed results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        for i, question in enumerate(self.questions):
            question_box = QVBoxLayout()
            question_box.setContentsMargins(10, 10, 10, 10)
            question_box.setSpacing(5)

            # Question header with time spent
            time_spent = self.question_times[i]
            question_header = QLabel(f"Question {i+1} (Time: {time_spent:.1f}s)")
            question_header.setStyleSheet("font-weight: bold;")
            question_box.addWidget(question_header)

            # Question text
            question_label = QLabel(question['question'])
            question_label.setWordWrap(True)
            question_box.addWidget(question_label)

            # User's answer and correctness
            user_answer_idx = question.get("user_answer", -1)
            if user_answer_idx == -1:
                answer_status = QLabel("Not answered")
                answer_status.setStyleSheet("color: #f0ad4e;")
            else:
                if question["is_correct"]:
                    answer_status = QLabel("Correct!")
                    answer_status.setStyleSheet("color: #5cb85c;")
                else:
                    answer_status = QLabel("Incorrect")
                    answer_status.setStyleSheet("color: #d9534f;")
            question_box.addWidget(answer_status)

            # Options with highlighting
            correct_answer = question["answer"]
            for j, option in enumerate(question["options"]):
                option_label = QLabel(option)
                if option.startswith(correct_answer + ")"):
                    option_label.setStyleSheet("color: #5cb85c; font-weight: bold;")
                elif j == user_answer_idx:
                    option_label.setStyleSheet("color: #d9534f;")
                question_box.addWidget(option_label)

            # Explanation if available
            if "explanation" in question:
                explanation_label = QLabel(f"Explanation: {question['explanation']}")
                explanation_label.setWordWrap(True)
                explanation_label.setStyleSheet("font-style: italic; color: #777;")
                question_box.addWidget(explanation_label)

            content_layout.addLayout(question_box)
            content_layout.addWidget(QLabel(""))  # Add space between questions

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(result_dialog.accept)
        layout.addWidget(close_btn)

        result_dialog.setLayout(layout)
        result_dialog.exec_()

class Task:
    def __init__(self, title="", description="", deadline="", level="easy", category="General", completion_date=""):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.level = level
        self.category = category
        self.status = "Pending"
        self.completion_date = completion_date  # Date when task is marked Completed
        if level == "hard":
            self.hardness = 3
        elif level == "medium":
            self.hardness = 2
        else:
            self.hardness = 1

    def get_hardness_level(self):
        if self.hardness == 3:
            return "Hard"
        if self.hardness == 2:
            return "Medium"
        return "Easy"

    def __lt__(self, other):
        if self.deadline != other.deadline:
            return self.deadline > other.deadline
        return self.hardness < other.hardness

class TaskGraph:
    def __init__(self):
        self.graph = {}  # Dictionary to store the graph {task_title: [connected_task_titles]}
    
    def add_task(self, task):
        """Add a task to the graph if it doesn't exist"""
        if task.title not in self.graph:
            self.graph[task.title] = []
    
    def add_relationship(self, task1_title, task2_title):
        """Create an undirected relationship between two tasks"""
        if task1_title not in self.graph:
            self.graph[task1_title] = []
        if task2_title not in self.graph:
            self.graph[task2_title] = []
        
        if task2_title not in self.graph[task1_title]:
            self.graph[task1_title].append(task2_title)
        if task1_title not in self.graph[task2_title]:
            self.graph[task2_title].append(task1_title)
    
    def get_related_tasks(self, task_title):
        """Get all tasks related to the given task"""
        return self.graph.get(task_title, [])
    
    def visualize(self):
        """Generate a visualization of the graph (for debugging)"""
        print("Task Relationships Graph:")
        for task, neighbors in self.graph.items():
            print(f"{task} -> {', '.join(neighbors) if neighbors else 'No connections'}")
    
    def find_connected_components(self):
        """Find all connected components in the graph"""
        visited = set()
        components = []
        
        for task in self.graph:
            if task not in visited:
                component = []
                stack = [task]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        stack.extend(self.graph[current])
                components.append(component)
        return components

class GraphVisualizationWidget(QWidget):
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Add control buttons
        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.draw_graph)
        btn_layout.addWidget(self.refresh_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial draw
        self.draw_graph()
    
    def draw_graph(self):
        """Draw the task relationship graph"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create a networkx graph
        G = nx.Graph()
        
        # Add nodes and edges from the task manager's graph
        for task_title, neighbors in self.task_manager.task_graph.graph.items():
            G.add_node(task_title)
            for neighbor in neighbors:
                G.add_edge(task_title, neighbor)
        
        if not G.nodes():
            ax.text(0.5, 0.5, "No tasks with relationships found", 
                   ha='center', va='center')
            self.canvas.draw()
            return
        
        # Get task categories for coloring
        node_colors = []
        for node in G.nodes():
            task = self.task_manager.get_task_by_title(node)
            if task:
                # Generate a color based on category name hash
                category_hash = hash(task.category) % 256
                node_colors.append(plt.cm.tab20(category_hash / 256))
            else:
                node_colors.append('gray')
        
        # Draw the graph
        pos = nx.spring_layout(G, k=0.5, iterations=50)  # Layout algorithm
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, ax=ax)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.5, edge_color='gray', ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif', ax=ax)
        
        # Add legend for categories
        unique_categories = set()
        for task_title in G.nodes():
            task = self.task_manager.get_task_by_title(task_title)
            if task:
                unique_categories.add(task.category)
        
        # Create custom legend
        legend_elements = []
        for category in sorted(unique_categories):
            color = plt.cm.tab20(hash(category) % 256 / 256)
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                            label=category, 
                                            markerfacecolor=color, markersize=10))
        
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Set title and adjust layout
        ax.set_title("Task Relationships Graph", fontsize=12)
        plt.tight_layout()
        
        self.canvas.draw()

class TaskHistory:
    def __init__(self):
        self.tasks = []
        self.MAX_SIZE = 100

    def is_empty(self):
        return len(self.tasks) == 0

    def is_full(self):
        return len(self.tasks) >= self.MAX_SIZE

    def add_to_history(self, task):
        if self.is_full():
            QMessageBox.warning(
                None, "Warning", "History is full, can't add task!")
            return False
        # Set completion date for Completed tasks
        if task.status == "Completed":
            task.completion_date = QDate.currentDate().toString("yyyy-MM-dd")
        self.tasks.append(task)
        return True

    def get_filtered_history(self, status=None, search_term="", category=None):
        tasks = self.tasks
        if status:
            tasks = [task for task in tasks if task.status == status]
        if search_term:
            tasks = [task for task in tasks if search_term.lower()
                     in task.title.lower()]
        if category:
            tasks = [task for task in tasks if task.category == category]
        return tasks

    def calculate_streak(self):
        if not self.tasks:
            return 0

        # Get all completed tasks with valid completion dates
        completed_tasks = [
            task for task in self.tasks
            if task.status == "Completed" and task.completion_date
        ]
        if not completed_tasks:
            return 0

        # Sort tasks by completion date (most recent first)
        completed_tasks.sort(key=lambda x: QDate.fromString(
            x.completion_date, "yyyy-MM-dd"), reverse=True)

        streak = 0
        current_date = QDate.currentDate()

        # Check for tasks on current day or previous days
        for i in range(365):  # Limit to one year to avoid infinite loops
            check_date = current_date.addDays(-i)
            date_str = check_date.toString("yyyy-MM-dd")
            has_task = any(task.completion_date ==
                           date_str for task in completed_tasks)

            if i == 0 and has_task:
                streak = 1  # Start with today if there's a task
            elif i > 0 and has_task:
                streak += 1  # Increment for each consecutive day with a task
            elif i > 0 and not has_task:
                break  # Break if a day is missing a completed task

        return streak

    def get_completed_tasks_count(self):
        """Returns the total number of completed tasks"""
        return len([task for task in self.tasks if task.status == "Completed"])

    def get_completed_tasks_today(self):
        """Returns the number of tasks completed today"""
        today = QDate.currentDate().toString("yyyy-MM-dd")
        return len([task for task in self.tasks
                    if task.status == "Completed" and task.completion_date == today])

    def get_completed_tasks(self):
        return [task for task in self.tasks if task.status == "Completed" and task.completion_date]

    def remove_task(self, task_title):
        for i, task in enumerate(self.tasks):
            if task.title == task_title:
                reply = QMessageBox.question(
                    None, 'Confirm',
                    f"Are you sure you want to remove this task?\nTitle: {task.title}\nStatus: {task.status}",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.tasks.pop(i)
                    return True
        return False

    def clear_history(self):
        reply = QMessageBox.question(None, 'Confirm',
                                     "Are you sure you want to clear the history?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.tasks.clear()
            return True
        return False

    def save_to_file(self, filename="history.csv"):
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                for task in self.tasks:
                    writer.writerow([
                        task.title, task.description, task.hardness, task.deadline,
                        task.status, task.category, task.completion_date
                    ])
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to save history: {str(e)}")
            return False

    def load_from_file(self, filename="history.csv"):
        if not os.path.exists(filename):
            return False

        try:
            self.tasks = []
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 5:
                        title, description, hardness_str, deadline, status = row[:5]
                        category = row[5] if len(row) > 5 else "General"
                        completion_date = row[6] if len(row) > 6 else ""
                        try:
                            hardness = int(hardness_str)
                            level = "hard" if hardness == 3 else "medium" if hardness == 2 else "easy"
                            task = Task(title, description, deadline,
                                        level, category, completion_date)
                            task.status = status
                            self.tasks.append(task)
                        except ValueError:
                            continue
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load history: {str(e)}")
            return False


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.task_history = TaskHistory()
        self.categories = {"General"}
        self.overdue_checker_running = True
        self.task_graph = TaskGraph()
        self.setup_overdue_checker()

    def setup_overdue_checker(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_overdue_tasks)
        self.timer.start(5000)
    


    def check_overdue_tasks(self):
        now = QDateTime.currentDateTime()
        overdue_tasks = []

        for task in self.tasks[:]:
            if self.is_overdue(task.deadline, now):
                task.status = "Overdue"
                self.task_history.add_to_history(task)
                overdue_tasks.append(task)
                self.tasks.remove(task)

        return overdue_tasks

    def is_overdue(self, deadline, current_time):
      try:
        deadline_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        current_dt = current_time.toPyDateTime()
        return deadline_dt < current_dt
      except ValueError:
        return False # Invalid deadline format, treat as not overdue

    def add_task(self, task):
        self.tasks.append(task)
        self.tasks.sort(reverse=True)
        if task.category not in self.categories:
            self.categories.add(task.category)
        self.task_graph.add_task(task)
        self.connect_related_tasks(task)
        
    def connect_related_tasks(self, new_task):
        """Connect the new task to other tasks in the same category"""
        for task in self.tasks:
            if task.title != new_task.title and task.category == new_task.category:
                self.task_graph.add_relationship(new_task.title, task.title)
    
    def get_related_tasks(self, task_title):
        """Get all tasks related to the given task"""
        return [self.get_task_by_title(title) for title in self.task_graph.get_related_tasks(task_title)]
    
    def visualize_task_relationships(self):
        """Visualize the task relationships (for debugging)"""
        self.task_graph.visualize()
    
    def find_task_clusters(self):
        """Find clusters of related tasks by category"""
        return self.task_graph.find_connected_components()    

    def get_task_by_title(self, title):
        for task in self.tasks:
            if task.title == title:
                return task
        return None

    def search_tasks(self, search_term):
        return [task for task in self.tasks
                if search_term.lower() in task.title.lower()]

    def remove_task(self, title):
        task = self.get_task_by_title(title)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def mark_task(self, title, status):
        task = self.get_task_by_title(title)
        if task:
            task.status = status
            if status in ["Completed", "Overdue", "Uncompleted"]:
                self.task_history.add_to_history(task)
                self.tasks.remove(task)
            return True
        return False

    def clear_tasks(self):
        self.tasks.clear()

    def add_category(self, category_name):
        if not category_name.strip():
            QMessageBox.warning(
                None, "Warning", "Category name cannot be empty!")
            return False
        if category_name in self.categories:
            QMessageBox.warning(None, "Warning", "Category already exists!")
            return False
        self.categories.add(category_name)
        return True

    def list_categories(self):
        return sorted(list(self.categories))

    def view_tasks_by_category(self, category):
        if category not in self.categories:
            return []
        return [task for task in self.tasks if task.category == category]

    def delete_category(self, category_name):
        if category_name not in self.categories:
            QMessageBox.warning(None, "Warning", "Category not found!")
            return False
        if category_name == "General":
            QMessageBox.warning(
                None, "Warning", "Cannot delete the default 'General' category!")
            return False
        for task in self.tasks:
            if task.category == category_name:
                QMessageBox.warning(None, "Warning",
                                    f"Cannot delete category '{category_name}' because it contains tasks. Move or delete tasks first.")
                return False
        self.categories.remove(category_name)
        return True

    def move_task_to_category(self, task_title, new_category):
        print(
            f"Debug: Attempting to move task '{task_title}' to category '{new_category}'")
        if new_category not in self.categories:
            print(
                f"Debug: Category '{new_category}' not found in {self.categories}")
            QMessageBox.warning(
                None, "Warning", "Target category does not exist!")
            return False
        task = self.get_task_by_title(task_title)
        if not task:
            print(f"Debug: Task '{task_title}' not found")
            QMessageBox.warning(None, "Warning", "Task not found!")
            return False
        task.category = new_category
        print(f"Debug: Task '{task_title}' moved to category '{new_category}'")
        return True

    def save_to_file(self, filename="tasks.csv"):
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["CATEGORIES"] + list(self.categories))
                for task in self.tasks:
                    writer.writerow([task.title, task.description, task.hardness,
                                    task.deadline, task.status, task.category, task.completion_date])
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to save tasks: {str(e)}")
            return False

    def load_from_file(self, filename="tasks.csv"):
        if not os.path.exists(filename):
            return False

        try:
            self.tasks = []
            self.categories = {"General"}
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                first_row = next(reader, None)
                if first_row and first_row[0] == "CATEGORIES":
                    self.categories.update(
                        [cat for cat in first_row[1:] if cat])

                for row in reader:
                    if len(row) >= 5:
                        title, description, hardness_str, deadline, status = row[:5]
                        category = row[5] if len(row) > 5 else "General"
                        completion_date = row[6] if len(row) > 6 else ""
                        try:
                            hardness = int(hardness_str)
                            level = "hard" if hardness == 3 else "medium" if hardness == 2 else "easy"
                            task = Task(title, description, deadline,
                                        level, category, completion_date)
                            task.status = status
                            self.tasks.append(task)
                            if category not in self.categories:
                                self.categories.add(category)
                        except ValueError:
                            continue
            self.tasks.sort(reverse=True)
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to load tasks: {str(e)}")
            return False


class AddTaskDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        # Use relative path for icon
        icon_path = os.path.join(os.path.dirname(__file__), "Tasks.jpg")
        self.setWindowIcon(QIcon(icon_path))
        self.setModal(True)
        self.categories = categories
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter task title")
        layout.addRow("Title:", self.title_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText(
            "Enter task description (max 200 chars)")
        self.desc_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.desc_edit)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["easy", "medium", "hard"])
        layout.addRow("Hardness Level:", self.level_combo)

        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.deadline_edit.setCalendarPopup(True)
        layout.addRow("Deadline:", self.deadline_edit)

        self.category_combo = QComboBox()
        self.category_combo.addItems(sorted(self.categories))
        self.category_combo.addItem("New Category...")
        self.category_combo.setCurrentText("General")
        layout.addRow("Category:", self.category_combo)

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

    def validate_and_accept(self):
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        category = self.category_combo.currentText()

        if not title:
            QMessageBox.warning(self, "Warning", "Task title cannot be empty!")
            return

        if len(description) > 200:
            QMessageBox.warning(
                self, "Warning", "Description cannot exceed 200 characters!")
            return

        if not any(c.isalpha() for c in description):
            QMessageBox.warning(
                self, "Warning", "Description must contain at least one letter!")
            return

        current_datetime = QDateTime.currentDateTime()
        if self.deadline_edit.dateTime() <= current_datetime:
            QMessageBox.warning(
                self, "Warning", "Deadline must be in the future!")
            return

        if category == "New Category...":
            new_category, ok = QInputDialog.getText(
                self, "New Category", "Enter new category name:")
            if not ok or not new_category.strip():
                QMessageBox.warning(
                    self, "Warning", "Category name cannot be empty!")
                return
            if new_category in self.categories:
                QMessageBox.warning(
                    self, "Warning", "Category already exists!")
                return
            self.category_combo.insertItem(
                self.category_combo.count() - 1, new_category)
            self.category_combo.setCurrentText(new_category)
            self.categories.add(new_category)
            category = new_category

        self.accept()

    def get_task(self):
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        level = self.level_combo.currentText()
        deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        category = self.category_combo.currentText()
        if category == "New Category...":
            category = "General"
        
        task = Task(title, description, deadline, level, category)
        
        # The TaskManager will handle connecting to related tasks
        return task


class EditTaskDialog(AddTaskDialog):
    def __init__(self, task, categories, parent=None):
        super().__init__(categories, parent)
        self.setWindowTitle("Edit Task")
        self.populate_fields(task)

    def populate_fields(self, task):
        self.title_edit.setText(task.title)
        self.desc_edit.setPlainText(task.description)

        index = self.level_combo.findText(task.level)
        if index >= 0:
            self.level_combo.setCurrentIndex(index)

        datetime = QDateTime.fromString(task.deadline, "yyyy-MM-dd HH:mm")
        if datetime.isValid():
            self.deadline_edit.setDateTime(datetime)

        index = self.category_combo.findText(task.category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.addItem(task.category)
            self.category_combo.setCurrentText(task.category)
            self.categories.add(task.category)


class TaskItemWidget(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        title_label = QLabel(f"<b>{self.task.title}</b>")
        title_label.setStyleSheet("font-size: 14px;")

        desc_label = QLabel(self.task.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555;")

        details_layout = QHBoxLayout()
        details_layout.addWidget(
            QLabel(f"<b>Deadline:</b> {self.task.deadline}"))
        details_layout.addStretch()
        details_layout.addWidget(
            QLabel(f"<b>Level:</b> {self.task.get_hardness_level()}"))
        details_layout.addStretch()
        details_layout.addWidget(QLabel(f"<b>Status:</b> {self.task.status}"))
        details_layout.addStretch()
        details_layout.addWidget(
            QLabel(f"<b>Category:</b> {self.task.category}"))

        if self.task.completion_date:
            details_layout.addStretch()
            details_layout.addWidget(
                QLabel(f"<b>Completed:</b> {self.task.completion_date}"))

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addLayout(details_layout)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
            }
            QWidget:hover {
                background-color: #f0f0f0;
            }
        """)


class TaskTitleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Task Title")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter task title")
        layout.addRow("Task Title:", self.title_edit)

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

    def validate_and_accept(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Warning", "Task title cannot be empty!")
            return
        self.accept()

    def get_title(self):
        return self.title_edit.text().strip()


class CategorySelectDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Target Category")
        self.setModal(True)
        self.categories = categories
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItems(sorted(self.categories))
        self.category_combo.setCurrentText("General")
        layout.addRow("Target Category:", self.category_combo)

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

    def get_category(self):
        return self.category_combo.currentText()


class StreakPage(QWidget):
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Streak Header
        self.streak_label = QLabel("Current Streak: 0 days")
        self.streak_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            padding: 10px;
        """)
        layout.addWidget(self.streak_label)

        # Progress Bar for Daily Goal
        self.progress_layout = QVBoxLayout()

        self.progress_label = QLabel("Daily Progress: 0/1 tasks completed")
        self.progress_label.setStyleSheet("font-size: 16px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v/%m tasks completed")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)

        self.progress_layout.addWidget(self.progress_label)
        self.progress_layout.addWidget(self.progress_bar)
        layout.addLayout(self.progress_layout)

        # Stats Section
        self.stats_frame = QFrame()
        self.stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_layout = QVBoxLayout()

        self.total_completed_label = QLabel("Total Completed Tasks: 0")
        self.today_completed_label = QLabel("Tasks Completed Today: 0")

        stats_layout.addWidget(self.total_completed_label)
        stats_layout.addWidget(self.today_completed_label)
        self.stats_frame.setLayout(stats_layout)
        layout.addWidget(self.stats_frame)

        # Motivational Message
        self.motivation_label = QLabel(
            "Keep it up! Complete a task today to grow your streak!")
        self.motivation_label.setStyleSheet("""
            font-size: 16px;
            color: #555;
            padding: 5px;
        """)
        layout.addWidget(self.motivation_label)

        # Completed Tasks List
        layout.addWidget(QLabel("<b>Recently Completed Tasks</b>"))
        self.completed_list = QListWidget()
        self.completed_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.completed_list)

        self.setLayout(layout)
        self.update_streak()

    def update_streak(self):
        streak = self.task_manager.task_history.calculate_streak()
        self.streak_label.setText(f"Current Streak: {streak} days")

        # Update progress bar
        completed_today = self.task_manager.task_history.get_completed_tasks_today()
        self.progress_bar.setMaximum(1)  # Default goal is 1 task per day
        self.progress_bar.setValue(completed_today)
        self.progress_label.setText(
            f"Daily Progress: {completed_today}/1 tasks completed")

        # Update stats
        total_completed = self.task_manager.task_history.get_completed_tasks_count()
        self.total_completed_label.setText(
            f"Total Completed Tasks: {total_completed}")
        self.today_completed_label.setText(
            f"Tasks Completed Today: {completed_today}")

        # Update motivational message based on streak and progress
        if streak == 0:
            self.motivation_label.setText(
                "Start a new streak today by completing a task!")
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + """
                QProgressBar::chunk {
                    background-color: #f44336;  /* Red for no progress */
                }
            """)
        elif completed_today >= 1:
            self.motivation_label.setText(
                "Great job! You've completed your daily goal!")
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + """
                QProgressBar::chunk {
                    background-color: #4CAF50;  /* Green for completed */
                }
            """)
        else:
            self.motivation_label.setText(
                f"Keep your {streak}-day streak going! Complete a task today!")
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + """
                QProgressBar::chunk {
                    background-color: #FFC107;  /* Yellow for in progress */
                }
            """)

        # Update completed tasks list
        self.completed_list.clear()
        completed_tasks = self.task_manager.task_history.get_completed_tasks()
        # Sort by completion date, most recent first
        completed_tasks.sort(key=lambda x: QDate.fromString(
            x.completion_date, "yyyy-MM-dd"), reverse=True)

        for task in completed_tasks[:10]:  # Show up to 10 recent tasks
            item = QListWidgetItem()
            widget = TaskItemWidget(task)
            item.setSizeHint(widget.sizeHint())
            self.completed_list.addItem(item)
            self.completed_list.setItemWidget(item, widget)

        if not completed_tasks:
            self.completed_list.addItem(
                "No completed tasks yet. Complete a task to start your streak!")


class CategoriesPage(QWidget):
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        layout.addWidget(QLabel("<b>Categories</b>"))
        layout.addWidget(self.category_list)

        btn_layout = QHBoxLayout()

        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_category)

        self.view_tasks_btn = QPushButton("View Tasks")
        self.view_tasks_btn.clicked.connect(self.view_tasks_by_category)

        self.delete_category_btn = QPushButton("Delete Category")
        self.delete_category_btn.clicked.connect(self.delete_category)

        self.move_task_btn = QPushButton("Move Task")
        self.move_task_btn.clicked.connect(self.move_task_to_category)

        btn_layout.addWidget(self.add_category_btn)
        btn_layout.addWidget(self.view_tasks_btn)
        btn_layout.addWidget(self.delete_category_btn)
        btn_layout.addWidget(self.move_task_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_category_list()

    def update_category_list(self):
        self.category_list.clear()
        for category in self.task_manager.list_categories():
            item = QListWidgetItem(category)
            self.category_list.addItem(item)

    def add_category(self):
        category_name, ok = QInputDialog.getText(
            self, "Add Category", "Enter category name:")
        if ok and category_name.strip():
            if self.task_manager.add_category(category_name.strip()):
                self.update_category_list()

    def view_tasks_by_category(self):
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a category!")
            return

        category = selected_items[0].text()
        tasks = self.task_manager.view_tasks_by_category(category)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tasks in Category: {category}")
        layout = QVBoxLayout()

        task_list = QListWidget()
        for task in tasks:
            item = QListWidgetItem()
            widget = TaskItemWidget(task)
            item.setSizeHint(widget.sizeHint())
            task_list.addItem(item)
            task_list.setItemWidget(item, widget)

        if not tasks:
            task_list.addItem("No tasks in this category.")

        layout.addWidget(task_list)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def delete_category(self):
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select a category to delete!")
            return

        category = selected_items[0].text()
        if self.task_manager.delete_category(category):
            self.update_category_list()

    def move_task_to_category(self):
        try:
            title_dialog = TaskTitleDialog(self)
            if title_dialog.exec_() != QDialog.Accepted:
                return

            task_title = title_dialog.get_title()
            if not task_title:
                QMessageBox.warning(
                    self, "Warning", "Task title cannot be empty!")
                return

            category_dialog = CategorySelectDialog(
                self.task_manager.categories, self)
            if category_dialog.exec_() != QDialog.Accepted:
                return

            target_category = category_dialog.get_category()

            if self.task_manager.move_task_to_category(task_title, target_category):
                QMessageBox.information(
                    self, "Success", f"Task '{task_title}' moved to category '{target_category}' successfully.")
                main_window = self.parent()
                while main_window and not isinstance(main_window, MainWindow):
                    main_window = main_window.parent()
                if main_window and hasattr(main_window, 'update_task_list'):
                    main_window.update_task_list()
                else:
                    QMessageBox.warning(
                        self, "Warning", "Unable to update task list. Please refresh manually.")
            else:
                QMessageBox.warning(
                    self, "Warning", "Failed to move task. Task may not exist or category is invalid.")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while moving the task: {str(e)}")
            print(f"Error in move_task_to_category: {str(e)}")


class SemesterSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Semester and Subject")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Semester selection
        semester_label = QLabel("Which semester are you in?")
        layout.addWidget(semester_label)

        self.semester_combo = QComboBox()
        self.semester_combo.addItems([
            "Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5"
        ])
        self.semester_combo.currentTextChanged.connect(self.update_ui)
        layout.addWidget(self.semester_combo)

        # Department selection (initially hidden)
        self.department_label = QLabel("Select department:")
        self.department_combo = QComboBox()
        self.department_combo.addItems(["AI", "CS", "SE"])
        self.department_combo.currentTextChanged.connect(self.update_subjects)
        
        # Initially hide department selection
        self.department_label.hide()
        self.department_combo.hide()
        
        layout.addWidget(self.department_label)
        layout.addWidget(self.department_combo)

        # Subject selection
        subject_label = QLabel("Select subject:")
        layout.addWidget(subject_label)

        self.subject_combo = QComboBox()
        layout.addWidget(self.subject_combo)

        # Initialize UI
        self.update_ui()

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)

        layout.addLayout(button_box)
        self.setLayout(layout)

    def update_ui(self):
        """Update the UI based on the selected semester"""
        semester = self.semester_combo.currentText()
        
        # Show/hide department selection based on semester
        if semester == "Semester 5":
            self.department_label.show()
            self.department_combo.show()
            self.update_subjects()
        else:
            self.department_label.hide()
            self.department_combo.hide()
            self.update_subjects()

    def update_subjects(self):
        """Update the subjects combo box based on the selected semester and department"""
        semester = self.semester_combo.currentText()
        self.subject_combo.clear()

        # Define subjects for each semester
        semester_subjects = {
            "Semester 1": [
                "Creativity & Innovation",
                "Introduction To Information System"
            ],
            "Semester 2": [
                "Problem Solving & Programming",
                "Discrete Structure"
            ],
            "Semester 3": [
                "Database System",
                "Object Oriented Programming"
            ],
            "Semester 4": [
                "Data Structure & Algorithms",
                "Introduction To Cyber Security"
            ],
            "Semester 5": {
                "AI": [
                    "Introduction to AI", 
                    "Machine Learning"
                ],
                "CS": [
                    "System Programming", 
                    "Theory Of Computing"
                ],
                "SE": [
                    "Software Project Management", 
                    "Software Design & Architecture"
                ]
            }
        }

        # Add subjects for the selected semester
        if semester == "Semester 5":
            department = self.department_combo.currentText()
            if department in semester_subjects[semester]:
                self.subject_combo.addItems(semester_subjects[semester][department])
        elif semester in semester_subjects:
            self.subject_combo.addItems(semester_subjects[semester])

    def get_semester(self):
        return self.semester_combo.currentText()

    def get_subject(self):
        return self.subject_combo.currentText()
    
    def get_department(self):
        if self.semester_combo.currentText() == "Semester 5":
            return self.department_combo.currentText()
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.task_manager = None  # Initialize later
        self.pomodoro_window = None
        self.ai_assistant = None
        self.setWindowTitle("Student Task Manager")
        icon_path = os.path.join(os.path.dirname(__file__), "Tasks.jpg")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 900, 600)

        self.task_manager = TaskManager()
        self.task_manager.load_from_file()
        self.task_manager.task_history.load_from_file()
        self.ai_assistant = AIAssistant(self.task_manager)

        self.setup_ui()

    def get_button_style(self):
        return """
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(152, 251, 203, 255),
                    stop:0.33 rgba(127, 207, 168, 255),
                    stop:0.66 rgba(85, 139, 113, 255),
                    stop:1 rgba(69, 110, 93, 255));
                color: Black;
                border-radius: 20px;
                padding: 8px 20px;
                border: none;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(152, 251, 203, 255),
                    stop:0.33 rgba(127, 207, 168, 255),
                    stop:0.66 rgba(95, 165, 135, 255),
                    stop:1 rgba(69, 110, 93, 255));
            }
            QPushButton:pressed {
                padding-top: 5px;
                padding-left: 5px;
                background-color: rgb(69, 110, 93);
            }
        """

    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Setup sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(152, 251, 203, 255),
                    stop:0.33 rgba(127, 207, 168, 255),
                    stop:0.66 rgba(85, 139, 113, 255),
                    stop:1 rgba(69, 110, 93, 255));
                border-radius: 20px;
                padding: 20px 40px;
                border: none;
                font-weight: bold;
                text-align: left;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Logo label
        logo_label = QLabel("Task Manager")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid rgba(69, 110, 93, 255);
            color: Black;
            background-color: transparent;
        """)
        sidebar_layout.addWidget(logo_label)


        btn = QPushButton("Generate Quiz")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\brain.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_creativity_innovation_quiz)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Task Options")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\task.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_task_options)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Tasks History")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\time-management.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_history)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Categories Management")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\classification.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_categories)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Streak")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\progress.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_streak)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Pomodoro Timer")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\stopwatch.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_pomodoro)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("AI Assistant")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\ai-assistant.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.show_ai_assistant)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Save and Exit")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\save.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.save_and_exit)
        sidebar_layout.addWidget(btn)
        
        btn = QPushButton("Exit Without Saving")
        btn.setStyleSheet(self.get_button_style())
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\switch.png"))
        btn.setIconSize(QSize(24, 24))
        btn.clicked.connect(self.exit_without_saving)
        sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        
        # Setup content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        # Create pages
        self.task_options_page = QWidget()
        self.setup_task_options_page()
        self.content_stack.addWidget(self.task_options_page)

        self.history_page = QWidget()
        self.setup_history_page()
        self.content_stack.addWidget(self.history_page)

        self.categories_page = CategoriesPage(self.task_manager, self)
        self.content_stack.addWidget(self.categories_page)

        self.streak_page = StreakPage(self.task_manager, self)
        self.content_stack.addWidget(self.streak_page)

        self.quiz_page = QuizPage(self)
        self.content_stack.addWidget(self.quiz_page)

        # AI Page
        self.ai_page = QWidget()
        self.setup_ai_page()
        self.content_stack.addWidget(self.ai_page)

        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)

    def setup_ai_page(self):
        layout = QVBoxLayout()
        self.ai_page.setLayout(layout)
        top_bar = QHBoxLayout()
        new_chat_btn = QPushButton(" New Chat")
        new_chat_btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\new-message.png"))  # You can also use your own icon path
        new_chat_btn.setFont(QFont("Segoe UI", 10))
        new_chat_btn.setCursor(Qt.PointingHandCursor)
        new_chat_btn.setStyleSheet("""
    QPushButton {
        background-color: #7f5af0;
        color: white;
        padding: 8px 14px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #5c3eea;
    }
""")
        new_chat_btn.clicked.connect(self.clear_chat)
        top_bar.addWidget(new_chat_btn)
    
    # Add stretch to push button to the left
        top_bar.addStretch()
    
        layout.addLayout(top_bar)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 11))
        self.chat_display.setStyleSheet("""
    QTextEdit {
        border: 2px solid #ddd;
        border-radius: 10px;
        background-color: #ffffff;
        padding: 10px;
    }
""")
        layout.addWidget(self.chat_display)

# Input area
        input_layout = QHBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setFont(QFont("Segoe UI", 11))
        self.user_input.setPlaceholderText("Ask me anything about System In the App...")
        self.user_input.setStyleSheet("""
    QLineEdit {
        border: 2px solid #ccc;
        border-radius: 8px;
        padding: 8px;
    }
""")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)

        send_btn = QPushButton("➤")
        send_btn.setFont(QFont("Arial", 14))
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
    QPushButton {
        background-color: #7f5af0;
        color: white;
        padding: 8px 14px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #5c3eea;
    }
""")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

# Initial greeting
        self.add_message("Apollo V1.0", random.choice(self.ai_assistant.responses["greetings"]))

    def setup_task_options_page(self):
        layout = QVBoxLayout()
        self.task_options_page.setLayout(layout)

        search_layout = QHBoxLayout()
        self.task_search_edit = QLineEdit()
        self.task_search_edit.setPlaceholderText("Search tasks...")
        self.task_search_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid rgba(69, 110, 93, 255);
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
            }
        """)
        self.task_search_edit.textChanged.connect(self.on_task_search)
        
        search_button = QPushButton("Search")
        search_button.setStyleSheet(self.get_button_style())
      
        search_button.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\search.png"))
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.clicked.connect(self.on_task_search)
        
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(self.get_button_style())
        clear_button.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete.png"))
        clear_button.setCursor(Qt.PointingHandCursor)
        clear_button.clicked.connect(self.clear_task_search)

        search_layout.addWidget(self.task_search_edit)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        layout.addLayout(search_layout)

        btn_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\task.png"
        if icon_path and os.path.exists(icon_path):
            self.add_task_btn.setIcon(QIcon(icon_path))
        self.add_task_btn.setCursor(Qt.PointingHandCursor)
        self.add_task_btn.clicked.connect(self.add_task)

        self.edit_task_btn = QPushButton("Edit Task")
        self.edit_task_btn.setStyleSheet(self.get_button_style())
        self.edit_task_btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\edit.png"))
        self.edit_task_btn.setCursor(Qt.PointingHandCursor)
        self.edit_task_btn.clicked.connect(self.edit_task)

        self.delete_task_btn = QPushButton("Delete Task")
        self.delete_task_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete11.png"
        if icon_path and os.path.exists(icon_path):
            self.delete_task_btn.setIcon(QIcon(icon_path))
        self.delete_task_btn.setCursor(Qt.PointingHandCursor)
        self.delete_task_btn.clicked.connect(self.delete_task)

        self.mark_task_btn = QPushButton("Mark Task")
        self.mark_task_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\marking.png"
        if icon_path and os.path.exists(icon_path):
            self.mark_task_btn.setIcon(QIcon(icon_path))
        self.mark_task_btn.setCursor(Qt.PointingHandCursor)
        self.mark_task_btn.clicked.connect(self.mark_task)
        
        self.related_tasks_btn = QPushButton("Show Related Tasks")
        self.related_tasks_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\relation.png"
        if icon_path and os.path.exists(icon_path):
            self.related_tasks_btn.setIcon(QIcon(icon_path))
        self.related_tasks_btn.setCursor(Qt.PointingHandCursor)
        self.related_tasks_btn.clicked.connect(self.show_related_tasks)
        
        self.visualize_btn = QPushButton("Visualize Task Relationships")
        self.visualize_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\knowledge-graph.png"
        if icon_path and os.path.exists(icon_path):
            self.visualize_btn.setIcon(QIcon(icon_path))
        self.visualize_btn.setCursor(Qt.PointingHandCursor)
        self.visualize_btn.clicked.connect(self.visualize_task_relationships)

        self.clear_tasks_btn = QPushButton("Clear All")
        self.clear_tasks_btn.setStyleSheet(self.get_button_style())
        self.clear_tasks_btn.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete.png"))
        self.clear_tasks_btn.setCursor(Qt.PointingHandCursor)
        self.clear_tasks_btn.clicked.connect(self.clear_tasks)

        btn_layout.addWidget(self.add_task_btn)
        btn_layout.addWidget(self.edit_task_btn)
        btn_layout.addWidget(self.delete_task_btn)
        btn_layout.addWidget(self.mark_task_btn)
        btn_layout.addWidget(self.related_tasks_btn)
        layout.addWidget(self.visualize_btn)
        btn_layout.addWidget(self.clear_tasks_btn)

        layout.addLayout(btn_layout)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 2px solid rgba(69, 110, 93, 255);
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
            }
        """)
        layout.addWidget(self.task_list)

        self.do_first_btn = QPushButton("Show Highest Priority Task")
        self.do_first_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\rank.png"
        if icon_path and os.path.exists(icon_path):
            self.do_first_btn.setIcon(QIcon(icon_path))
        self.do_first_btn.setCursor(Qt.PointingHandCursor)
        self.do_first_btn.clicked.connect(self.show_highest_priority)
        layout.addWidget(self.do_first_btn)

    def setup_history_page(self):
        layout = QVBoxLayout()
        self.history_page.setLayout(layout)

        search_layout = QHBoxLayout()
        self.history_search_edit = QLineEdit()
        self.history_search_edit.setPlaceholderText("Search history...")
        self.history_search_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid rgba(69, 110, 93, 255);
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
            }
        """)
        self.history_search_edit.textChanged.connect(self.on_history_search)
        
        search_button = QPushButton("Search")
        search_button.setStyleSheet(self.get_button_style())
        search_button.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\search.png"))
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.clicked.connect(self.on_history_search)
        
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(self.get_button_style())
        clear_button.setIcon(QIcon(r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete.png"))
        clear_button.setCursor(Qt.PointingHandCursor)
        clear_button.clicked.connect(self.clear_history_search)

        search_layout.addWidget(self.history_search_edit)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        layout.addLayout(search_layout)

        filter_layout = QHBoxLayout()

        self.all_history_btn = QPushButton("All Tasks")
        self.all_history_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\task.png"
        if icon_path and os.path.exists(icon_path):
            self.all_history_btn.setIcon(QIcon(icon_path))
        self.all_history_btn.setCursor(Qt.PointingHandCursor)
        self.all_history_btn.clicked.connect(lambda: self.update_history_list())

        self.completed_btn = QPushButton("Completed")
        self.completed_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\checklist.png"
        if icon_path and os.path.exists(icon_path):
            self.completed_btn.setIcon(QIcon(icon_path))
        self.completed_btn.setCursor(Qt.PointingHandCursor)
        self.completed_btn.clicked.connect(lambda: self.update_history_list("Completed"))

        self.uncompleted_btn = QPushButton("Uncompleted")
        self.uncompleted_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\remove.png"
        if icon_path and os.path.exists(icon_path):
            self.uncompleted_btn.setIcon(QIcon(icon_path))
        self.uncompleted_btn.setCursor(Qt.PointingHandCursor)
        self.uncompleted_btn.clicked.connect(lambda: self.update_history_list("Uncompleted"))

        self.overdue_btn = QPushButton("Overdue")
        self.overdue_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\over-time.png"
        if icon_path and os.path.exists(icon_path):
            self.overdue_btn.setIcon(QIcon(icon_path))
        self.overdue_btn.setCursor(Qt.PointingHandCursor)
        self.overdue_btn.clicked.connect(lambda: self.update_history_list("Overdue"))

        filter_layout.addWidget(self.all_history_btn)
        filter_layout.addWidget(self.completed_btn)
        filter_layout.addWidget(self.uncompleted_btn)
        filter_layout.addWidget(self.overdue_btn)

        layout.addLayout(filter_layout)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 2px solid rgba(69, 110, 93, 255);
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
            }
        """)
        layout.addWidget(self.history_list)

        manage_layout = QHBoxLayout()

        self.remove_task_btn = QPushButton("Remove Task")
        self.remove_task_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete.png"
        if icon_path and os.path.exists(icon_path):
            self.remove_task_btn.setIcon(QIcon(icon_path))
        self.remove_task_btn.setCursor(Qt.PointingHandCursor)
        self.remove_task_btn.clicked.connect(self.remove_history_task)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\delete.png"
        if icon_path and os.path.exists(icon_path):
            self.clear_history_btn.setIcon(QIcon(icon_path))
        self.clear_history_btn.setCursor(Qt.PointingHandCursor)
        self.clear_history_btn.clicked.connect(self.clear_history)

        manage_layout.addWidget(self.remove_task_btn)
        manage_layout.addWidget(self.clear_history_btn)

        layout.addLayout(manage_layout)

    # Other methods (unchanged, included for completeness)
    def clear_chat(self):
        self.chat_display.clear()
        self.add_message("Apollo V1.0", random.choice(self.ai_assistant.responses["greetings"]))
        
    def add_message(self, sender, message):
        current_text = self.chat_display.toPlainText()
        if current_text:
            current_text += "\n\n"
        current_text += f"<b>{sender}:</b> {message}"
        self.chat_display.setHtml(current_text)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def send_message(self):
        user_text = self.user_input.text().strip()
        if user_text:
            self.add_message("You", user_text)
            response = self.ai_assistant.get_response(user_text)
            self.add_message("Apollo", response)
            self.user_input.clear()

    def show_ai_assistant(self):
        self.content_stack.setCurrentWidget(self.ai_page)
     
    def show_pomodoro(self):
        if self.pomodoro_window is None:
            self.pomodoro_window = PomodoroApp(self.task_manager)
        self.pomodoro_window.show()
        self.pomodoro_window.raise_()
        self.pomodoro_window.activateWindow()

    def show_creativity_innovation_quiz(self):
        semester_dialog = SemesterSelectDialog(self)
        if semester_dialog.exec_() != QDialog.Accepted:
            return  # User canceled

        semester = semester_dialog.get_semester()
        subject = semester_dialog.get_subject()

        subject_data = {
            "Creativity & Innovation": {
                "file_path": os.path.join(os.path.dirname(__file__), "creativity_innovation_question_bank.json"),
                "quiz_key": "Creativity and Innovation"
            },
            "Introduction To Information System": {
                "file_path": os.path.join(os.path.dirname(__file__), "Introduction_to_Information_System.json"),
                "quiz_key": "Introduction to Information Systems"
            },
            "Problem Solving & Programming": {
                "file_path": os.path.join(os.path.dirname(__file__), "problem solving.json"),
                "quiz_key": "Problem Solving"
            },
            "Discrete Structure": {
                "file_path": os.path.join(os.path.dirname(__file__), "Discrete.json"),
                "quiz_key": "Discrete_Mathematics"
            },
            "Database System": {
                "file_path": os.path.join(os.path.dirname(__file__), "database.json"),
                "quiz_key": "Database_System"
            },
            "Object Oriented Programming": {
                "file_path": os.path.join(os.path.dirname(__file__), "oop.json"),
                "quiz_key": "OOP"
            },
            "Data Structure & Algorithms": {
                "file_path": os.path.join(os.path.dirname(__file__), "data_Structure.json"),
                "quiz_key": "DataStructure"
            },
            "Introduction To Cyber Security": {
                "file_path": os.path.join(os.path.dirname(__file__), "cyber_security.json"),
                "quiz_key": "CyberSecurity"
            },
            "System Programming": {
                "file_path": os.path.join(os.path.dirname(__file__), "ststem_programming_sem5.json"),
                "quiz_key": "SystemProgramming"
            },
            "Theory Of Computing": {
                "file_path": os.path.join(os.path.dirname(__file__), "theroy_of_computing_sem5.json"),
                "quiz_key": "Theory"
            },
            "Software Project Management": {
                "file_path": os.path.join(os.path.dirname(__file__), "spm_questions.json"),
                "quiz_key": "Software_Project_Management"
            },
            "Software Design & Architecture": {
                "file_path": os.path.join(os.path.dirname(__file__), "sdr_questions (1).json"),
                "quiz_key": "Software_Design&Arch"
            },
            "Introduction to AI": {
                "file_path": os.path.join(os.path.dirname(__file__), "AI_Multiple_Choice_Questions_150.json"),
                "quiz_key": "IntroductionToAi"
            },
            "Machine Learning": {
                "file_path": os.path.join(os.path.dirname(__file__), "Machine_Learning_MCQ_Batch1.json"),
                "quiz_key": "Machine_Learning"
            }
        }

        if subject not in subject_data:
            QMessageBox.warning(self, "Error", f"Unsupported subject: {subject}")
            return

        file_path = subject_data[subject]["file_path"]
        quiz_key = subject_data[subject]["quiz_key"]

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")

            with open(file_path, "r", encoding='utf-8') as file:
                data = json.load(file)

            if quiz_key not in data:
                raise KeyError(f"The key '{quiz_key}' was not found in the JSON file.")

            all_questions = data[quiz_key]
            random.shuffle(all_questions)
            selected_questions = all_questions[:20]

            self.content_stack.setCurrentWidget(self.quiz_page)
            self.quiz_page.load_questions(selected_questions)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load quiz: {str(e)}")
            print(f"Error loading quiz: {str(e)}")

    def show_related_tasks(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a task first!")
            return
            
        selected_index = self.task_list.row(selected_items[0])
        task = self.task_manager.tasks[selected_index]
        
        related_tasks = self.task_manager.get_related_tasks(task.title)
        
        if not related_tasks:
            QMessageBox.information(self, "Related Tasks", 
                                   f"No related tasks found for '{task.title}'")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tasks Related to: {task.title}")
        layout = QVBoxLayout()
        
        label = QLabel(f"Tasks related to '{task.title}' (same category: {task.category}):")
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: rgba(69, 110, 93, 255);
            }
        """)
        layout.addWidget(label)
        
        task_list = QListWidget()
        task_list.setStyleSheet("""
            QListWidget {
                border: 2px solid rgba(69, 110, 93, 255);
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
            }
        """)
        for related_task in related_tasks:
            item = QListWidgetItem()
            widget = TaskItemWidget(related_task)
            item.setSizeHint(widget.sizeHint())
            task_list.addItem(item)
            task_list.setItemWidget(item, widget)
        
        layout.addWidget(task_list)
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\like.png"
        if icon_path and os.path.exists(icon_path):
            ok_btn.setIcon(QIcon(icon_path))
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def visualize_task_relationships(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Task Relationships Graph")
        dialog.resize(800, 600)
    
        layout = QVBoxLayout()
        dialog.setLayout(layout)
    
        graph_widget = GraphVisualizationWidget(self.task_manager, dialog)
        layout.addWidget(graph_widget)
    
        info_label = QLabel(
            "Nodes represent tasks. Edges connect related tasks (usually in the same category).\n"
            "Tasks with the same color belong to the same category."
        )
        info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: rgba(69, 110, 93, 255);
                background-color: transparent;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
    
        dialog.exec_()

    def show_task_options(self):
        self.content_stack.setCurrentWidget(self.task_options_page)
        self.update_task_list()

    def show_history(self):
        self.content_stack.setCurrentWidget(self.history_page)
        self.update_history_list()

    def show_categories(self):
        self.content_stack.setCurrentWidget(self.categories_page)
        self.categories_page.update_category_list()

    def show_streak(self):
        self.content_stack.setCurrentWidget(self.streak_page)
        self.streak_page.update_streak()

    def update_task_list(self, tasks=None):
        self.task_list.clear()
        tasks_to_show = tasks if tasks is not None else self.task_manager.tasks[:]
        for task in tasks_to_show:
            item = QListWidgetItem()
            widget = TaskItemWidget(task)
            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def update_history_list(self, status_filter=None):
        self.history_list.clear()

        tasks = self.task_manager.task_history.get_filtered_history(
            status_filter,
            self.history_search_edit.text().strip()
        )

        for task in reversed(tasks):
            item = QListWidgetItem()
            widget = TaskItemWidget(task)
            item.setSizeHint(widget.sizeHint())
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, widget)

    def remove_history_task(self):
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select a task to remove!")
            return

        selected_index = self.history_list.row(selected_items[0])
        actual_index = len(
            self.task_manager.task_history.tasks) - 1 - selected_index

        if 0 <= actual_index < len(self.task_manager.task_history.tasks):
            task = self.task_manager.task_history.tasks[actual_index]

            if self.task_manager.task_history.remove_task(task.title):
                self.update_history_list()
                if self.content_stack.currentWidget() == self.streak_page:
                    self.streak_page.update_streak()
        else:
            QMessageBox.warning(
                self, "Warning", "Selected task no longer exists!")

    def clear_history(self):
        if self.task_manager.task_history.clear_history():
            self.update_history_list()
            if self.content_stack.currentWidget() == self.streak_page:
                self.streak_page.update_streak()

    def on_task_search(self):
        search_term = self.task_search_edit.text().strip()
        if search_term:
            found_tasks = self.task_manager.search_tasks(search_term)
            self.update_task_list(found_tasks)
        else:
            self.update_task_list()

    def clear_task_search(self):
        self.task_search_edit.clear()
        self.update_task_list()

    def on_history_search(self):
        self.update_history_list()

    def clear_history_search(self):
        self.history_search_edit.clear()
        self.update_history_list()

    def add_task(self):
        dialog = AddTaskDialog(self.task_manager.categories, self)
        if dialog.exec_() == QDialog.Accepted:
            task = dialog.get_task()
            self.task_manager.add_task(task)
            self.update_task_list()

    def edit_task(self):
        if not self.task_manager.tasks:
            QMessageBox.warning(self, "Warning", "No tasks available to edit!")
            return

        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select a task to edit!")
            return

        selected_index = self.task_list.row(selected_items[0])
        task = self.task_manager.tasks[selected_index]

        dialog = EditTaskDialog(task, self.task_manager.categories, self)
        if dialog.exec_() == QDialog.Accepted:
            edited_task = dialog.get_task()
            edited_task.status = task.status

            self.task_manager.tasks[selected_index] = edited_task
            self.task_manager.tasks.sort(reverse=True)
            self.update_task_list()

    def delete_task(self):
        if not self.task_manager.tasks:
            QMessageBox.warning(self, "Warning", "No tasks available to delete!")
            return

        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a task to delete!")
            return

        selected_index = self.task_list.row(selected_items[0])
        task = self.task_manager.tasks[selected_index]

        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete this task?\nTitle: {task.title}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.task_manager.tasks.pop(selected_index)
            self.update_task_list()

    def mark_task(self):
        if not self.task_manager.tasks:
            QMessageBox.warning(self, "Warning", "No tasks available to mark!")
            return

        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Warning", "Please select a task to mark!")
            return

        selected_index = self.task_list.row(selected_items[0])
        task = self.task_manager.tasks[selected_index]

        status, ok = QInputDialog.getItem(
            self, "Mark Task", "Select new status:",
            ["Pending", "Completed", "Overdue", "Uncompleted"], 0, False
        )

        if ok and status:
            self.task_manager.mark_task(task.title, status)
            self.update_task_list()
            self.update_history_list()
            if status == "Completed":
                self.streak_page.update_streak()

    def clear_tasks(self):
        if not self.task_manager.tasks:
            QMessageBox.warning(self, "Warning", "No tasks to clear!")
            return

        reply = QMessageBox.question(
            self, 'Confirm Clear',
            "Are you sure you want to clear all tasks?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.task_manager.clear_tasks()
            self.update_task_list()

    def show_highest_priority(self):
        if not self.task_manager.tasks:
            QMessageBox.warning(self, "Warning", "No tasks available!")
            return

        highest_task = max(self.task_manager.tasks)
        self.show_task_details(highest_task, "Highest Priority Task")

    def show_task_details(self, task, title="Task Details"):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        title_label = QLabel(task.title)
        title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: rgba(69, 110, 93, 255);
        """)
        form_layout.addRow("Title:", title_label)

        desc_label = QLabel(task.description)
        desc_label.setStyleSheet("""
            color: rgba(69, 110, 93, 255);
        """)
        desc_label.setWordWrap(True)
        form_layout.addRow("Description:", desc_label)

        form_layout.addRow("Deadline:", QLabel(task.deadline))
        form_layout.addRow("Hardness Level:", QLabel(task.get_hardness_level()))
        form_layout.addRow("Status:", QLabel(task.status))
        form_layout.addRow("Category:", QLabel(task.category))

        if task.completion_date:
            form_layout.addRow("Completed On:", QLabel(task.completion_date))

        layout.addLayout(form_layout)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(self.get_button_style())
        icon_path = ""
        if icon_path and os.path.exists(icon_path):
            ok_btn.setIcon(QIcon(icon_path))
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_and_exit(self):
        if self.task_manager.save_to_file() and self.task_manager.task_history.save_to_file():
            self.show_exit_message()
            self.close()

    def exit_without_saving(self):
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            "Are you sure you want to exit without saving?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.show_exit_message()
            self.close()

    def show_exit_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Thank You")
        msg.setText("""
            <center>
                <h2>Thanks for using our program!</h2>
                <p>By: Mayer-Basmala-Menna-3bshafy-Galal-Ahmed</p>
                <p>To Dr.Tamer</p>
            </center>
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        ok_btn = msg.button(QMessageBox.Ok)
        ok_btn.setStyleSheet(self.get_button_style())
        icon_path = r"C:\Users\EL-MOHANDES\Desktop\guiProject\like.png"
        if icon_path and os.path.exists(icon_path):
            ok_btn.setIcon(QIcon(icon_path))
        ok_btn.setCursor(Qt.PointingHandCursor)
        msg.exec_()
        msg = QMessageBox(self)
        msg.setWindowTitle("Thank You")
        msg.setText("""
            <center>
                <h2>Thanks for using our program!</h2>
                <p>By: Mayer-Basmala-Menna-3bshafy-Galal-Ahmed</p>
                <p>To Dr.Tamer</p>
            </center>
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        ok_btn = msg.button(QMessageBox.Ok)
        ok_btn.setStyleSheet(self.get_button_style())
        ok_btn.setCursor(Qt.PointingHandCursor)
        msg.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            "Do you want to save before exiting?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if reply == QMessageBox.Save:
            if self.task_manager.save_to_file() and self.task_manager.task_history.save_to_file():
                event.accept()
            else:
                event.ignore()
        elif reply == QMessageBox.Discard:
            event.accept()
        else:
            event.ignore()


class VerificationManager:
    def __init__(self):
        self.verification_file = "verification_codes.csv"

    def generate_verification_code(self, email):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        expiration = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRE_MINUTES)
        try:
            file_exists = os.path.exists(self.verification_file)
            with open(self.verification_file, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['email', 'code', 'expiration'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    'email': email,
                    'code': code,
                    'expiration': expiration.strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"Error saving verification code: {str(e)}")
            return None
        return code

    def verify_code(self, email, code):
        try:
            with open(self.verification_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['email'] == email and row['code'] == code:
                        expiration = datetime.strptime(row['expiration'], "%Y-%m-%d %H:%M:%S")
                        if datetime.now() <= expiration:
                            return True
        except FileNotFoundError:
            return False
        return False

    def send_verification_email(self, email, code):
        try:
            subject = "Email Verification Code"
            body = f"""
            <html>
                <body>
                    <h2>Your Verification Code✅</h2>
                    <p>🧐Please use the following code to verify your email address:</p>
                    <h3 style="color: #1e6b6f;">{code}</h3>
                    <p>This code will expire in {VERIFICATION_EXPIRE_MINUTES} minutes.</p>
                    <p>Thanks For Using Our Student Task Manager System ❤️.</p>
                </body>
            </html>
            """
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            return False

class EncryptionManager:
    def __init__(self):
        self.key_file = "encryption_key.key"
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)

    def _get_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.cipher_suite.encrypt(data).decode()

    def decrypt(self, encrypted_data):
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher_suite.decrypt(encrypted_data).decode()

class UserManager:
    def __init__(self):
        self.filename = "users.csv"
        self.encryption = EncryptionManager()
        self.verification = VerificationManager()

    def register_user(self, username, email, password):
        if self.user_exists(username, email):
            return False, "Username or email already exists"
        encrypted_password = self.encryption.encrypt(password)
        verification_code = self.verification.generate_verification_code(email)
        if not verification_code:
            return False, "Failed to generate verification code"
        if not self.verification.send_verification_email(email, verification_code):
            return False, "Failed to send verification email"
        try:
            file_exists = os.path.exists(self.filename)
            with open(self.filename, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['username', 'email', 'password', 'verified'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    'username': username,
                    'email': email,
                    'password': encrypted_password,
                    'verified': 'False'
                })
            return True, f"Registration successful. Verification email sent to {email}"
        except Exception as e:
            return False, f"Error saving user: {str(e)}"

    def verify_user_email(self, email, code):
        if self.verification.verify_code(email, code):
            try:
                users = []
                verified = False
                with open(self.filename, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['email'] == email:
                            row['verified'] = 'True'
                            verified = True
                        users.append(row)
                if verified:
                    with open(self.filename, 'w', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=['username', 'email', 'password', 'verified'])
                        writer.writeheader()
                        writer.writerows(users)
                    return True, "Email verified successfully!"
                return False, "Email not found in our records"
            except Exception as e:
                return False, f"Error updating verification status: {str(e)}"
        return False, "Invalid or expired verification code."

    def user_exists(self, username, email):
        try:
            with open(self.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username or row['email'] == email:
                        return True
        except FileNotFoundError:
            return False
        return False

    def authenticate_user(self, username, password):
        try:
            with open(self.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username:
                        if row.get('verified', 'False').lower() != 'true':
                            return False, "Email not verified. Please check your email."
                        try:
                            decrypted_password = self.encryption.decrypt(row['password'])
                            if decrypted_password == password:
                                return True, "Login successful"
                        except:
                            return False, "Invalid credentials"
            return False, "Invalid username or password"
        except FileNotFoundError:
            return False, "No users registered yet"
        except Exception as e:
            return False, f"Error during authentication: {str(e)}"

class SecurityAlert(QMessageBox):
    def __init__(self, title, message, alert_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)

        if alert_type == QMessageBox.Icon.Critical:
            self.setup_error_style()
        elif alert_type == QMessageBox.Icon.Information:
            self.setup_success_style()
        else:
            self.setup_default_style()

        self.setWindowIcon(QIcon(self.create_security_icon(alert_type)))
        self.add_security_tips(message)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        ok_button = self.button(QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)

    def setup_error_style(self):
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 20px;
                padding: 8px 20px;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(30, 123, 111, 255), stop:1 rgba(95, 112, 228, 255));
                color: white;
                border-radius: 10px;
                padding: 4px 12px;
                min-width: 60px;
                max-width: 80px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #1e6b6f;
            }
            QMessageBox QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(25, 103, 91, 255), stop:1 rgba(85, 102, 218, 255));
            }
            QMessageBox QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 83, 71, 255), stop:1 rgba(75, 92, 208, 255));
                border: 1px inset #1e6b6f;
            }
        """)

    def setup_success_style(self):
        self.setIcon(QMessageBox.Icon.Information)
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 20px;
                padding: 8px 20px;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(30, 123, 111, 255), stop:1 rgba(95, 112, 228, 255));
                color: white;
                border-radius: 10px;
                padding: 4px 12px;
                min-width: 60px;
                max-width: 80px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #1e6b6f;
            }
            QMessageBox QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(25, 103, 91, 255), stop:1 rgba(85, 102, 218, 255));
            }
            QMessageBox QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 83, 71, 255), stop:1 rgba(75, 92, 208, 255));
                border: 1px inset #1e6b6f;
            }
        """)

    def setup_default_style(self):
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 20px;
                padding: 8px 20px;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(30, 123, 111, 255), stop:1 rgba(95, 112, 228, 255));
                color: white;
                border-radius: 10px;
                padding: 4px 12px;
                min-width: 60px;
                max-width: 80px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #1e6b6f;
            }
            QMessageBox QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(25, 103, 91, 255), stop:1 rgba(85, 102, 218, 255));
            }
            QMessageBox QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 83, 71, 255), stop:1 rgba(75, 92, 208, 255));
                border: 1px inset #1e6b6f;
            }
        """)

    def create_security_icon(self, alert_type):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if alert_type == QMessageBox.Icon.Critical:
            painter.setBrush(QColor("#ff5555"))
            painter.setPen(QColor("#ff5555"))
            painter.drawEllipse(0, 0, 32, 32)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(8, 24, "!")
        elif alert_type == QMessageBox.Icon.Information:
            painter.setBrush(QColor("#50fa7b"))
            painter.setPen(QColor("#50fa7b"))
            painter.drawEllipse(0, 0, 32, 32)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(12, 24, "✓")
        else:
            painter.setBrush(QColor("#3298dc"))
            painter.setPen(QColor("#3298dc"))
            painter.drawEllipse(0, 0, 32, 32)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(12, 24, "i")

        painter.end()
        return pixmap

    def add_security_tips(self, message):
        if "password" in message.lower():
            self.setDetailedText(
                "🔒 Security Tips:\n• Use at least 12 characters\n• Mix letters, numbers & symbols\n• Avoid common words\n• Don't reuse passwords")
        elif "username" in message.lower():
            self.setDetailedText(
                "👤 Username Tips:\n• 3-20 characters\n• Letters and numbers only\n• Avoid personal info")
        elif "email" in message.lower():
            self.setDetailedText(
                "📧 Email Tips:\n• Use a valid, accessible email\n• We'll send verification links\n• Keep your email secure")
        elif "invalid" in message.lower() and "login" in message.lower():
            self.setDetailedText(
                "⚠️ Account Protection:\n• Check Caps Lock\n• Try resetting password\n• Contact support if locked out")

class VerificationWindow(QWidget):
    def __init__(self, email, user_manager, parent=None):
        super().__init__(parent)
        self.email = email
        self.user_manager = user_manager
        self.setWindowTitle("Email Verification")
        self.setGeometry(300, 300, 400, 250)
        
        layout = QVBoxLayout()
        
        self.label = QLabel(f"Enter verification code sent to {email}")
        layout.addWidget(self.label)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Verification Code")
        layout.addWidget(self.code_input)
        
        self.verify_button = QPushButton("Verify")
        self.verify_button.clicked.connect(self.handle_verification)
        layout.addWidget(self.verify_button)
        
        self.resend_button = QPushButton("Resend Code")
        self.resend_button.clicked.connect(self.handle_resend_code)
        layout.addWidget(self.resend_button)
        
        self.setLayout(layout)
    
    def handle_verification(self):
        code = self.code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Please enter the verification code")
            return
            
        success, message = self.user_manager.verify_user_email(self.email, code)
        if success:
            QMessageBox.information(self, "Success", message)
            self.close()
            # Open main application window or login window here if needed
        else:
            QMessageBox.critical(self, "Error", message)
    
    def handle_resend_code(self):
        # Generate a new verification code and send it
        verification_code = self.user_manager.verification.generate_verification_code(self.email)
        if verification_code:
            if self.user_manager.verification.send_verification_email(self.email, verification_code):
                QMessageBox.information(self, "Success", "New verification code has been sent to your email")
            else:
                QMessageBox.critical(self, "Error", "Failed to send new verification code")
        else:
            QMessageBox.critical(self, "Error", "Failed to generate new verification code")

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = WelcomeUI()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(self.open_login)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def show_message(self, title, message, icon):
        alert = SecurityAlert(title, message, icon, self)
        alert.exec()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginUI()
        self.ui.setupUi(self)
        self.user_manager = UserManager()
        self.ui.pushButton.clicked.connect(self.handle_login)
        self.ui.pushButton_2.clicked.connect(self.open_register)

    def handle_login(self):
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        if not username or not password:
            self.show_message("Error", "Please enter both username and password", QMessageBox.Icon.Critical)
            return

        success, message = self.user_manager.authenticate_user(username, password)
        if success:
            self.show_message("Success", message, QMessageBox.Icon.Information)
            window = MainWindow()
            window.show()
        else:
            self.show_message("Error", message, QMessageBox.Icon.Critical)

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

    def show_message(self, title, message, icon):
        alert = SecurityAlert(title, message, icon, self)
        alert.exec()


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = RegisterUI()
        self.ui.setupUi(self)
        self.user_manager = UserManager()
        self.ui.pushButton.clicked.connect(self.handle_register)
        self.ui.pushButton_2.clicked.connect(self.open_login)
        self.ui.user_name.textChanged.connect(self.validate_username)
        self.ui.lineEdit_4.textChanged.connect(self.validate_email)
        self.ui.lineEdit_2.textChanged.connect(self.validate_passwords)
        self.ui.lineEdit_3.textChanged.connect(self.validate_passwords)

        self.ui.user_name.setPlaceholderText("Username")
        self.ui.lineEdit_4.setPlaceholderText("Email")
        self.ui.lineEdit_2.setPlaceholderText("Password")
        self.ui.lineEdit_3.setPlaceholderText("Confirm Password")

    def validate_username(self, text):
        username_exists = False
        try:
            with open(self.user_manager.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == text:
                        username_exists = True
                        break
        except FileNotFoundError:
            username_exists = False

        is_valid = len(text) >= 3 and not username_exists if text else False
        border_color = "rgba(0, 200, 0, 0.8)" if is_valid else "rgba(255, 0, 0, 0.8)" if text else "rgba(46, 82, 101, 0.8)"
        self.ui.user_name.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            border-bottom: 2px solid {border_color};
            color: rgba(0, 0, 0, 0.8);
            padding-bottom: 7px;
        """)

    def validate_email(self, text):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        email_exists = False
        try:
            with open(self.user_manager.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['email'] == text:
                        email_exists = True
                        break
        except FileNotFoundError:
            email_exists = False

        is_valid = re.match(pattern, text) is not None and not email_exists if text else False
        border_color = "rgba(0, 200, 0, 0.8)" if is_valid else "rgba(255, 0, 0, 0.8)" if text else "rgba(46, 82, 101, 0.8)"
        self.ui.lineEdit_4.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            border-bottom: 2px solid {border_color};
            color: rgba(0, 0, 0, 0.8);
            padding-bottom: 7px;
        """)

    def validate_passwords(self):
        password = self.ui.lineEdit_2.text()
        confirm = self.ui.lineEdit_3.text()
        passwords_match = password == confirm if (password and confirm) else None
        pass1_color = "rgba(0, 200, 0, 0.8)" if passwords_match is True else "rgba(255, 0, 0, 0.8)" if passwords_match is False else "rgba(46, 82, 101, 0.8)"
        pass2_color = pass1_color
        self.ui.lineEdit_2.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            border-bottom: 2px solid {pass1_color};
            color: rgba(0, 0, 0, 0.8);
            padding-bottom: 7px;
        """)
        self.ui.lineEdit_3.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            border-bottom: 2px solid {pass2_color};
            color: rgba(0, 0, 0, 0.8);
            padding-bottom: 7px;
        """)

    def handle_register(self):
        username = self.ui.user_name.text()
        email = self.ui.lineEdit_4.text()
        password = self.ui.lineEdit_2.text()
        confirm_password = self.ui.lineEdit_3.text()

        if not all([username, email, password, confirm_password]):
            self.show_message("Error", "All fields are required", QMessageBox.Icon.Critical)
            return

        if len(username) < 3:
            self.show_message("Error", "Username must be at least 3 characters", QMessageBox.Icon.Critical)
            return

        username_exists = False
        try:
            with open(self.user_manager.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username:
                        username_exists = True
                        break
        except FileNotFoundError:
            username_exists = False

        if username_exists:
            self.show_message("Error", "The username you have provided is already associated with an account. Please use a different username.", QMessageBox.Icon.Critical)
            return

        email_exists = False
        try:
            with open(self.user_manager.filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['email'] == email:
                        email_exists = True
                        break
        except FileNotFoundError:
            email_exists = False

        if email_exists:
            self.show_message("Error", "The email you have provided is already associated with an account. Sign in or reset your password.", QMessageBox.Icon.Critical)
            return

        if password != confirm_password:
            self.show_message("Error", "Passwords do not match", QMessageBox.Icon.Critical)
            return

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.show_message("Error", "Please enter a valid email address", QMessageBox.Icon.Critical)
            return

        success, message = self.user_manager.register_user(username, email, password)
        if success:
            self.show_message("Success", message, QMessageBox.Icon.Information)
            self.verification_window = VerificationWindow(email, self.user_manager)
            self.verification_window.show()
        else:
            self.show_message("Error", message, QMessageBox.Icon.Critical)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def show_message(self, title, message, icon):
        alert = SecurityAlert(title, message, icon, self)
        alert.exec()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec())