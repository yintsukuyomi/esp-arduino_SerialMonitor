import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QTabWidget, QGroupBox, QFormLayout
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime  # Import for timestamps
import threading  # Import threading for non-blocking serial reading

class SerialMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.auto_scroll = True
        self.reading_thread = None  # Thread for serial reading
        self.reading_active = False  # Flag to control the thread
        self.language = "en"  # Default language is English
        self.translations = {
            "en": {
                "title": "ESP32 Serial Monitor",
                "port_label": "Select Port:",
                "baud_label": "Baud Rate:",
                "connect": "Connect",
                "disconnect": "Disconnect",
                "clear_output": "Clear Output",
                "save_output": "Save Output",
                "auto_scroll": "Auto Scroll: On",
                "status_ready": "Ready",
                "status_connected": "Serial connection active.",
                "status_disconnected": "Serial connection disconnected.",
                "status_error": "Connection error.",
                "output_saved": "Output saved to 'serial_output.txt'.",
                "output_save_error": "Error saving output.",
                "exit": "Exit",
                "connection_status_waiting": "Connection Status: Waiting",
                "connection_status_connected": "Connection Status: Connected",
                "connection_status_disconnected": "Connection Status: Disconnected",
                "connection_status_error": "Connection Status: Error",
                "tooltip_port": "Select the port to connect.",
                "tooltip_baud": "Select the baud rate for the connection.",
                "tooltip_connect": "Connect to the selected port and baud rate.",
                "tooltip_disconnect": "Disconnect the current connection.",
                "tooltip_clear": "Clear the output area.",
                "tooltip_save": "Save the output to a file.",
                "tooltip_auto_scroll": "Toggle auto-scroll on/off.",
                "tooltip_exit": "Close the application."
            },
            "jp": {
                "title": "ESP32 シリアルモニター",
                "port_label": "ポートを選択:",
                "baud_label": "ボーレート:",
                "connect": "接続",
                "disconnect": "切断",
                "clear_output": "出力をクリア",
                "save_output": "出力を保存",
                "auto_scroll": "自動スクロール: オン",
                "status_ready": "準備完了",
                "status_connected": "シリアル接続がアクティブです。",
                "status_disconnected": "シリアル接続が切断されました。",
                "status_error": "接続エラー。",
                "output_saved": "出力が 'serial_output.txt' に保存されました。",
                "output_save_error": "出力の保存中にエラーが発生しました。",
                "exit": "終了",
                "connection_status_waiting": "接続状況: 待機中",
                "connection_status_connected": "接続状況: 接続済み",
                "connection_status_disconnected": "接続状況: 切断済み",
                "connection_status_error": "接続状況: エラー",
                "tooltip_port": "接続するポートを選択してください。",
                "tooltip_baud": "接続のボーレートを選択してください。",
                "tooltip_connect": "選択したポートとボーレートに接続します。",
                "tooltip_disconnect": "現在の接続を切断します。",
                "tooltip_clear": "出力エリアをクリアします。",
                "tooltip_save": "出力をファイルに保存します。",
                "tooltip_auto_scroll": "自動スクロールのオン/オフを切り替えます。",
                "tooltip_exit": "アプリケーションを閉じます。"
            }
        }
        self.current_theme = "dark"  # Default theme
        self.themes = {
            "dark": """
                QWidget {
                    background-color: #0a0a0a;
                    color: #e0e0e0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    font-size: 14px;
                    padding: 5px;
                    color: #4d9ef9;
                    font-weight: 500;
                }
                QComboBox {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a1a1a, stop:1 #252525);
                    border: 1px solid #2c4766;
                    border-radius: 6px;
                    padding: 8px;
                    min-width: 180px;
                    font-size: 13px;
                    selection-background-color: #1d4ed8;
                }
                QTextEdit {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f0f0f, stop:1 #1a1a1a);
                    border: 2px solid #1e3a5f;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    selection-background-color: #1d4ed8;
                }
                QPushButton {
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1e40af, stop:1 #3b82f6);
                    color: white;
                }
            """,
            "light": """
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    font-size: 14px;
                    padding: 5px;
                    color: #333333;
                    font-weight: 500;
                }
                QComboBox {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 8px;
                    min-width: 180px;
                    font-size: 13px;
                    selection-background-color: #0078d7;
                }
                QTextEdit {
                    background-color: #f9f9f9;
                    border: 1px solid #cccccc;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    selection-background-color: #0078d7;
                }
                QPushButton {
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """,
            "blue": """
                QWidget {
                    background-color: #001f3f;
                    color: #ffffff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QLabel {
                    font-size: 14px;
                    padding: 5px;
                    color: #7fdbff;
                    font-weight: 500;
                }
                QComboBox {
                    background-color: #003366;
                    border: 1px solid #00509e;
                    border-radius: 6px;
                    padding: 8px;
                    min-width: 180px;
                    font-size: 13px;
                    selection-background-color: #0078d7;
                }
                QTextEdit {
                    background-color: #00264d;
                    border: 1px solid #00509e;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    selection-background-color: #0078d7;
                }
                QPushButton {
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """
        }
        self.initUI()

    def refresh_ports(self):
        """Bağlantıdaki mevcut portları tazeleyip combo box'a ekler."""
        self.port_selector.clear()  # Önceki portları temizle
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)  # Port adlarını ekle

    def initUI(self):
        self.setWindowTitle(self.translations[self.language]["title"])
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(self.translations[self.language]["title"])
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4d9ef9;
                padding: 10px;
                text-align: center;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Tabs for Settings and Monitor
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; }")
        layout.addWidget(tabs)

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)

        # Port and Baud Rate Group
        port_baud_group = QGroupBox(self.translations[self.language]["title"])
        port_baud_layout = QFormLayout()
        self.port_label = QLabel(self.translations[self.language]["port_label"])
        self.port_selector = QComboBox()
        self.port_selector.setToolTip(self.translations[self.language]["tooltip_port"])
        self.refresh_ports()
        port_baud_layout.addRow(self.port_label, self.port_selector)

        self.baud_label = QLabel(self.translations[self.language]["baud_label"])
        self.baud_selector = QComboBox()
        self.baud_selector.setToolTip(self.translations[self.language]["tooltip_baud"])
        self.baud_selector.addItems(["115200", "9600", "19200", "38400", "57600", "115200"])
        port_baud_layout.addRow(self.baud_label, self.baud_selector)

        port_baud_group.setLayout(port_baud_layout)
        settings_layout.addWidget(port_baud_group)

        # Buttons Group
        buttons_group = QGroupBox("Actions")
        buttons_layout = QHBoxLayout()
        self.connect_button = QPushButton(self.translations[self.language]["connect"])
        self.connect_button.setToolTip(self.translations[self.language]["tooltip_connect"])
        self.connect_button.clicked.connect(self.connect_serial)
        buttons_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton(self.translations[self.language]["disconnect"])
        self.disconnect_button.setToolTip(self.translations[self.language]["tooltip_disconnect"])
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        buttons_layout.addWidget(self.disconnect_button)

        self.clear_button = QPushButton(self.translations[self.language]["clear_output"])
        self.clear_button.setToolTip(self.translations[self.language]["tooltip_clear"])
        self.clear_button.clicked.connect(self.clear_output)
        buttons_layout.addWidget(self.clear_button)

        self.save_button = QPushButton(self.translations[self.language]["save_output"])
        self.save_button.setToolTip(self.translations[self.language]["tooltip_save"])
        self.save_button.clicked.connect(self.save_output)
        buttons_layout.addWidget(self.save_button)

        buttons_group.setLayout(buttons_layout)
        settings_layout.addWidget(buttons_group)

        # Auto Scroll Checkbox
        self.auto_scroll_checkbox = QPushButton(self.translations[self.language]["auto_scroll"])
        self.auto_scroll_checkbox.setCheckable(True)
        self.auto_scroll_checkbox.setChecked(self.auto_scroll)
        self.auto_scroll_checkbox.setToolTip(self.translations[self.language]["tooltip_auto_scroll"])
        self.auto_scroll_checkbox.clicked.connect(self.toggle_auto_scroll)
        settings_layout.addWidget(self.auto_scroll_checkbox)

        # Theme and Language Group
        theme_language_group = QGroupBox("Preferences")
        theme_language_layout = QFormLayout()
        theme_selector = QComboBox()
        theme_selector.addItems(["Dark", "Light", "Blue"])
        theme_selector.setToolTip("Select the application theme.")
        theme_selector.currentIndexChanged.connect(self.change_theme)
        theme_language_layout.addRow("Theme:", theme_selector)

        language_selector = QComboBox()
        language_selector.addItems(["English", "日本語"])
        language_selector.setToolTip("Select the application language.")
        language_selector.currentIndexChanged.connect(self.change_language)
        theme_language_layout.addRow("Language:", language_selector)

        theme_language_group.setLayout(theme_language_layout)
        settings_layout.addWidget(theme_language_group)

        tabs.addTab(settings_tab, "Settings")

        # Monitor Tab
        monitor_tab = QWidget()
        monitor_layout = QVBoxLayout()
        monitor_tab.setLayout(monitor_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setToolTip("Serial data will appear here.")
        monitor_layout.addWidget(self.output)

        self.status_bar = QLabel(self.translations[self.language]["status_ready"])
        self.status_bar.setStyleSheet("color: #9da5b4; font-size: 14px; padding: 5px;")
        monitor_layout.addWidget(self.status_bar)

        tabs.addTab(monitor_tab, "Monitor")

        # Connection Status Label
        self.connection_status_label = QLabel(self.translations[self.language]["connection_status_waiting"])
        self.connection_status_label.setStyleSheet("color: #9da5b4; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.connection_status_label)

        # Exit Button
        self.quit_button = QPushButton(self.translations[self.language]["exit"])
        self.quit_button.setToolTip(self.translations[self.language]["tooltip_exit"])
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

        # Apply the default theme
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name):
        """Apply the selected theme."""
        self.setStyleSheet(self.themes[theme_name])

    def change_theme(self, index):
        """Change the application theme."""
        theme_names = ["dark", "light", "blue"]
        self.current_theme = theme_names[index]
        self.apply_theme(self.current_theme)

    def update_ui_text(self):
        """Update UI text based on the selected language."""
        t = self.translations[self.language]
        self.setWindowTitle(t["title"])
        self.port_label.setText(t["port_label"])
        self.baud_label.setText(t["baud_label"])
        self.connect_button.setText(t["connect"])
        self.disconnect_button.setText(t["disconnect"])
        self.clear_button.setText(t["clear_output"])
        self.save_button.setText(t["save_output"])
        self.auto_scroll_checkbox.setText(t["auto_scroll"])
        self.quit_button.setText(t["exit"])
        self.connection_status_label.setText(t["connection_status_waiting"])
        self.status_bar.setText(t["status_ready"])
        self.port_selector.setToolTip(t["tooltip_port"])
        self.baud_selector.setToolTip(t["tooltip_baud"])
        self.connect_button.setToolTip(t["tooltip_connect"])
        self.disconnect_button.setToolTip(t["tooltip_disconnect"])
        self.clear_button.setToolTip(t["tooltip_clear"])
        self.save_button.setToolTip(t["tooltip_save"])
        self.auto_scroll_checkbox.setToolTip(t["tooltip_auto_scroll"])
        self.quit_button.setToolTip(t["tooltip_exit"])

    def change_language(self, index):
        """Change the application language."""
        self.language = "en" if index == 0 else "jp"
        self.update_ui_text()

    def connect_serial(self):
        """Connect to the selected serial port."""
        port_name = self.port_selector.currentText()
        baud_rate = int(self.baud_selector.currentText())

        if not port_name:
            self.append_output("Please select a port to connect!")
            return

        try:
            self.serial_port = serial.Serial(port_name, baud_rate, timeout=1)
            self.append_output(f"Connected to {port_name} ({baud_rate} baud)")
            self.connection_status_label.setText(self.translations[self.language]["connection_status_connected"])
            self.connection_status_label.setStyleSheet("color: #22c55e; font-size: 16px; font-weight: bold;")
            self.status_bar.setText(self.translations[self.language]["status_connected"])

            # Start the reading thread
            self.reading_active = True
            self.reading_thread = threading.Thread(target=self.read_serial_thread, daemon=True)
            self.reading_thread.start()
        except Exception as e:
            self.append_output(f"Error: {e}")
            self.connection_status_label.setText(self.translations[self.language]["connection_status_error"])
            self.connection_status_label.setStyleSheet("color: #ef4444; font-size: 16px; font-weight: bold;")
            self.status_bar.setText(self.translations[self.language]["status_error"])

    def disconnect_serial(self):
        """Disconnect from the serial port."""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.reading_active = False  # Stop the reading thread
                self.serial_port.close()
                self.append_output("Disconnected.")
                self.connection_status_label.setText(self.translations[self.language]["connection_status_disconnected"])
                self.connection_status_label.setStyleSheet("color: #9da5b4; font-size: 16px; font-weight: bold;")
                self.status_bar.setText(self.translations[self.language]["status_disconnected"])
            else:
                self.append_output("Already disconnected.")
        except Exception as e:
            self.append_output(f"Error during disconnection: {e}")

    def read_serial_thread(self):
        """Read data from the serial port in a separate thread."""
        try:
            while self.reading_active:
                if self.serial_port and self.serial_port.is_open:
                    try:
                        data = self.serial_port.readline().decode().strip()
                        if data:
                            self.append_output(data)
                    except Exception as e:
                        self.append_output(f"Error reading data: {e}")
                        self.disconnect_serial()
                        break
        except Exception as e:
            self.append_output(f"Thread error: {e}")

    def clear_output(self):
        """Clear the output area."""
        self.output.clear()

    def toggle_auto_scroll(self):
        """Toggle auto-scroll functionality."""
        self.auto_scroll = not self.auto_scroll
        status = "Açık" if self.auto_scroll else "Kapalı"
        self.auto_scroll_checkbox.setText(f"Otomatik Kaydırma: {status}")

    def save_output(self):
        """Save the output to a text file."""
        try:
            with open("serial_output.txt", "w", encoding="utf-8") as file:
                file.write(self.output.toPlainText())
            self.append_output(self.translations[self.language]["output_saved"])
        except Exception as e:
            self.append_output(f"{self.translations[self.language]['output_save_error']}: {e}")

    def append_output(self, message):
        """Append a message to the output area with a timestamp."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.output.append(f"[{timestamp}] {message}")
            if self.auto_scroll:
                self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())
        except Exception as e:
            print(f"Error appending output: {e}")

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            self.reading_active = False  # Stop the thread
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            event.accept()
        except Exception as e:
            self.append_output(f"Error during close: {e}")
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec())
