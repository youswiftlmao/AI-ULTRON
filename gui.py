import sys
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
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
        self.timer = QTimer(self)
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

        glow.setColorAt(
            0.0,
            QColor(255, 170, 40, 180)
        )
        
        glow.setColorAt(
            0.35,
            QColor(255, 120, 0, 80)
        )

        glow.setColorAt(
            1.0,
            QColor(255, 80, 0, 0)
        )

        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
            int(center_x - 130),
            int(center_y - 130),
            260,
            260
        )

        #orbiting rings of the orb oooo
        painter.save()

        painter.translate(center_x, center_y)

        for ring in range(3):
            ring_angle = math.radians(
                self.angle * (1 if ring % 2 == 0 else-1)
                + ring * 60
            )

            painter.save()

            painter.rotate(
                math.degrees(ring_angle)
            )

            #vertical thingie
            width_ring =  150 + ring * 25
            height_ring =  150 + ring * 15

            pen = QPen(
                QColor(255, 140, 0, 170 - ring * 25)
            )

            pen.setWidth(2)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            painter.drawEllipse(
                int(-width_ring / 2),
                int(-height_ring / 2),
                width_ring,
                height_ring
            )

            #cool tech marker
            painter.setPen(
                QPen(
                    QColor(255, 150, 40, 180),
                    2
                )
            )

            painter.drawPoint(
                int(width_ring / 2 ),
                0

            )

            painter.restore()

        painter.restore()


        #the inside enery core thing

        core_gradient = QRadialGradient(
            center_x,
            center_y,
            orb_radius
        )

        core_gradient.setColorAt(
            0.0,
            QColor(255, 245, 210, 255)

        )


        core_gradient.setColorAt(
                0.25,
                QColor(255, 180, 50, 255)
            )

        core_gradient.setColorAt(
                0.65,
                QColor(255, 100, 0, 220)
            )

        core_gradient.setColorAt(
                1.0,
                QColor(120, 30, 0, 0)
            )

        painter.setBrush(core_gradient)
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
            int(center_x - orb_radius),
            int(center_y - orb_radius),
            int(orb_radius * 2),
            int(orb_radius * 2)
        )


        #ring of core

        painter.setBrush(Qt.NoBrush)

        painter.setPen(
            QPen(
                QColor(255, 180, 60, 220),
                3
            )

        )

        painter.drawEllipse(
                int(center_x - orb_radius - 8),
                int(center_y - orb_radius - 8),
                int((orb_radius + 8) * 2),
                int((orb_radius + 8) * 2)
            )

        painter.end()

class UltronWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setWindowTitle("ULTRON")
        self.resize(850, 550)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        central.setLayout(layout)

        title = QLabel("ULTRON")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 36, QFont.Bold))

        status = QLabel("● SYSTEM ONLINE")
        status.setAlignment(Qt.AlignCenter)
        status.setFont(QFont("Arial", 16))

        core = HologramCore()

        layout.addWidget(title)
        layout.addWidget(status)
        layout.addWidget(core, 1)

        central.setStyleSheet("""
            QWidget {
                background-color: rgba(12, 8, 5, 205);
                color: #ff8c00;
                border: 1px solid rgba(255, 120, 20, 100);
                border-radius: 18px;
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