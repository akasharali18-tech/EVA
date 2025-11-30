"""
EVA Voice Assistant - PyQt5 Professional GUI
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QTextEdit, QLabel,
                              QFrame, QLineEdit, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from datetime import datetime
from ui_bridge import EVABridge

class ListenThread(QThread):
    """Thread for listening to voice commands"""
    command_received = pyqtSignal(str)
    
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.is_running = True
    
    def run(self):
        while self.is_running:
            command = self.bridge.listen()
            if command:
                self.command_received.emit(command)
    
    def stop(self):
        self.is_running = False

class EVAMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bridge = EVABridge()
        self.is_active = False
        self.listen_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("EVA - Voice Assistant")
        self.setGeometry(100, 100, 900, 700)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Consolas", 11))
        main_layout.addWidget(self.chat_area)
        
        # Controls
        controls = self.create_controls()
        main_layout.addWidget(controls)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Timer for clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Welcome message
        self.add_message("EVA", "Hello! Click 'Activate' to start.", "bot")
    
    def set_dark_theme(self):
        """Apply dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 46))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(45, 45, 68))
        palette.setColor(QPalette.AlternateBase, QColor(61, 61, 92))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(61, 61, 92))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)
    
    def create_header(self):
        """Create header section"""
        header = QFrame()
        header.setFrameStyle(QFrame.Box)
        header.setStyleSheet("background-color: #2d2d44; border-radius: 10px;")
        
        layout = QHBoxLayout()
        header.setLayout(layout)
        
        # Title
        title = QLabel("🤖 EVA - Electronic Voice Assistant")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ffff;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("● INACTIVE")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_label.setStyleSheet("color: #ff4444;")
        layout.addWidget(self.status_label)
        
        return header
    
    def create_controls(self):
        """Create control buttons"""
        controls = QFrame()
        layout = QHBoxLayout()
        controls.setLayout(layout)
        
        # Activate button
        self.activate_btn = QPushButton("🎤 ACTIVATE EVA")
        self.activate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: black;
                border-radius: 8px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #00dd77;
            }
        """)
        self.activate_btn.clicked.connect(self.toggle_activation)
        layout.addWidget(self.activate_btn)
        
        # Manual button
        manual_btn = QPushButton("⌨️ MANUAL INPUT")
        manual_btn.setFont(QFont("Arial", 11))
        manual_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d5c;
                color: white;
                border-radius: 8px;
                padding: 15px 20px;
            }
            QPushButton:hover {
                background-color: #4d4d6c;
            }
        """)
        manual_btn.clicked.connect(self.open_manual_input)
        layout.addWidget(manual_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ CLEAR")
        clear_btn.setFont(QFont("Arial", 11))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d5c;
                color: white;
                border-radius: 8px;
                padding: 15px 20px;
            }
            QPushButton:hover {
                background-color: #4d4d6c;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        layout.addWidget(clear_btn)
        
        return controls
    
    def add_message(self, sender, text, msg_type):
        """Add message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "user":
            color = "#00ff88"
        elif msg_type == "bot":
            color = "#00ffff"
        else:
            color = "#ffaa00"
        
        html = f'<span style="color: #666;">[{timestamp}]</span> '
        html += f'<span style="color: {color}; font-weight: bold;">{sender}:</span> '
        html += f'<span style="color: white;">{text}</span><br><br>'
        
        self.chat_area.append(html)
    
    def toggle_activation(self):
        """Toggle activation"""
        if not self.is_active:
            self.is_active = True
            self.status_label.setText("● ACTIVE - LISTENING")
            self.status_label.setStyleSheet("color: #00ff88;")
            self.activate_btn.setText("🔴 DEACTIVATE EVA")
            self.activate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border-radius: 8px;
                    padding: 15px 30px;
                }
            """)
            self.add_message("SYSTEM", "EVA activated and listening...", "system")
            self.start_listening()
        else:
            self.is_active = False
            self.status_label.setText("● INACTIVE")
            self.status_label.setStyleSheet("color: #ff4444;")
            self.activate_btn.setText("🎤 ACTIVATE EVA")
            self.activate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00ff88;
                    color: black;
                    border-radius: 8px;
                    padding: 15px 30px;
                }
            """)
            self.add_message("SYSTEM", "EVA deactivated.", "system")
            if self.listen_thread:
                self.listen_thread.stop()
    
    def start_listening(self):
        """Start listening thread"""
        self.listen_thread = ListenThread(self.bridge)
        self.listen_thread.command_received.connect(self.handle_command)
        self.listen_thread.start()
    
    def handle_command(self, command):
        """Handle received command"""
        self.add_message("YOU", command, "user")
        
        if "eva" in command:
            self.add_message("EVA", "Yes, I'm listening...", "bot")
            self.bridge.speak("Yes, I'm listening")
        else:
            result = self.bridge.process_command(command)
            if result:
                self.add_message("EVA", result, "bot")
                self.bridge.speak(result)
    
    def open_manual_input(self):
        """Open manual input dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual Command Input")
        dialog.setGeometry(200, 200, 400, 150)
        
        layout = QVBoxLayout()
        
        label = QLabel("Enter your command:")
        layout.addWidget(label)
        
        input_field = QLineEdit()
        layout.addWidget(input_field)
        
        btn_layout = QHBoxLayout()
        
        submit_btn = QPushButton("Execute")
        submit_btn.clicked.connect(lambda: self.submit_manual(input_field.text(), dialog))
        btn_layout.addWidget(submit_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def submit_manual(self, command, dialog):
        """Submit manual command"""
        if command.strip():
            self.add_message("YOU", command + " (manual)", "user")
            result = self.bridge.process_command(command)
            if result:
                self.add_message("EVA", result, "bot")
                self.bridge.speak(result)
        dialog.close()
    
    def clear_chat(self):
        """Clear chat area"""
        self.chat_area.clear()
        self.add_message("SYSTEM", "Chat cleared.", "system")
    
    def update_time(self):
        """Update time in status bar"""
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.statusBar().showMessage(f"Ready | {current_time}")

def main():
    app = QApplication(sys.argv)
    window = EVAMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()