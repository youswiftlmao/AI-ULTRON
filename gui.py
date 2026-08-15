import sys
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)

class HologramCore(QWidget):
    def __init__(self):
        super().__init__()

        self.angle = 0 
        self.pulse = 0

        #animation timer
        self.timerEvent = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def animate(self):
        self.angle += 1

        if self.angle >= 360:
            self.angle = 0

        self.pulse += 0.05

        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        center_x = width / 2
        center_y = height / 2


        #the core/ orb pusles
        pulse_size = 1 + math.sin(self.pulse) * 0.08

        orb_radius = 55* pulse_size

        #orb glowwww

        glow = QRadialGradient(
            center_x,
            center_y,
            130
        )
        