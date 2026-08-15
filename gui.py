import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
)

class UltronWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setWindowTitle("ULTRON")
        self.resize(850, 550)

        #the main window

        central = QWidget()
        self.setCentralWidget(central)


        layout = QVBoxLayout()
        central.setLayout(layout)

        #main title text
        title = QLabel("ULTRON")
        title.setAlignment(Qt.AlignCenter)

        title__font = QFont("Arial", 36, QFont.Bold)
        title.setFont(title__font)

        #state / status gulp 
        status = QLabel("● SYSTEM ONLINE")
        status.setAlignment(Qt.AlignCenter)

        status_font = QFont("Arial", 18)
        status.setFont(status_font)

        #main stuff
        core = QLabel("ULTRON CORE")
        core.setAlignment(Qt.AlignCenter)

        core_font = QFont("Arial", 28, QFont.Bold)
        core.setFont(core_font)

        layout.addWidget(title)
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(core)
        layout.addStretch()

        #holografic display
        central.setStyleSheet("""
            QWidget {
                background-color: rgba(35, 18, 5, 210);
                color: #ff8c00;
                border: 1px solid rgba(255, 140, 0, 120);
                border-radius: 20px;
            }

            QLabel {
                color: #ff8c00;
                background-color: transparent;
                border: none;
            }
        """)

app = QApplication(sys.argv)

window = UltronWindow()
window.show()

sys.exit(app.exec())