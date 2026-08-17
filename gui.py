import sys
import math
import random

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QSurfaceFormat
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QFrame
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *


# OpenGL settings
format = QSurfaceFormat()
format.setRenderableType(QSurfaceFormat.OpenGL)
format.setProfile(QSurfaceFormat.CompatibilityProfile)
format.setVersion(2, 1)
format.setDepthBufferSize(24)
format.setSwapInterval(1)
QSurfaceFormat.setDefaultFormat(format)


class HologramCore(QOpenGLWidget):

    def __init__(self):
        super().__init__()

        self.setAutoFillBackground(False)

        self.angle = 0
        self.time = 0

        self.vertices, self.edges = self.create_sphere(
            0.90, 12, 24
        )

        self.beams = self.create_beams(
            24, 2.25
        )

        self.particles = []

        for _ in range(180):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            radius = random.uniform(0.92, 1.45)

            self.particles.append((
                radius * math.sin(phi) * math.cos(theta),
                radius * math.sin(phi) * math.sin(theta),
                radius * math.cos(phi)
            ))

        self.ambient = []

        for _ in range(60):
            self.ambient.append([
                random.uniform(1.8, 2.6),
                random.uniform(0, 2 * math.pi),
                random.uniform(-0.004, 0.004)
            ])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)

    def create_sphere(self, radius, rings, segments):
        vertices = []
        edges = []

        for i in range(rings + 1):
            lat = math.pi * (i / rings - 0.5)

            for j in range(segments):
                lon = 2 * math.pi * j / segments

                x = radius * math.cos(lon) * math.cos(lat)
                y = radius * math.sin(lon) * math.cos(lat)
                z = radius * math.sin(lat)

                vertices.append((x, y, z))

        for i in range(rings):
            for j in range(segments):
                p = i * segments + j
                next_p = i * segments + (j + 1) % segments

                edges.append((p, next_p))
                edges.append((p, p + segments))

        return vertices, edges

    def create_beams(self, count, length):
        beams = []

        for _ in range(count):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)

            beams.append((
                length * math.sin(phi) * math.cos(theta),
                length * math.sin(phi) * math.sin(theta),
                length * math.cos(phi)
            ))

        return beams

    def initializeGL(self):
        glClearColor(0.070, 0.047, 0.031, 1.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    def resizeGL(self, width, height):
        height = max(height, 1)

        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(
            45.0,
            width / height,
            0.1,
            50.0
        )

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(0, 0, -6)
        glDisable(GL_DEPTH_TEST)

        self.draw_ambient()
        self.draw_spikes()

        glPushMatrix()

        glRotatef(
            self.angle,
            0.35,
            1.0,
            0.15
        )

        # glowing core
        self.glow(95, 0.018)
        self.glow(65, 0.045)
        self.glow(42, 0.12)
        self.glow(25, 0.30)
        self.glow(17, 1.0)

        glLineWidth(1.0)
        glBegin(GL_LINES)

        for a, b in self.edges:
            glColor4f(1.0, 0.42, 0.03, 0.75)

            glVertex3fv(self.vertices[a])
            glVertex3fv(self.vertices[b])

        glEnd()

        glPointSize(2.0)
        glBegin(GL_POINTS)

        glColor4f(1.0, 0.65, 0.12, 0.85)

        for vertex in self.vertices:
            glVertex3fv(vertex)

        glEnd()
        glPopMatrix()

        glPushMatrix()

        glRotatef(
            -self.angle * 0.35,
            0.2,
            1.0,
            0.4
        )

        glPointSize(2.0)
        glBegin(GL_POINTS)

        glColor4f(1.0, 0.50, 0.05, 0.55)

        for particle in self.particles:
            glVertex3fv(particle)

        glEnd()
        glPopMatrix()

        self.draw_rings()
        self.draw_beams()

        glEnable(GL_DEPTH_TEST)

    def glow(self, size, alpha):
        glPointSize(size)
        glBegin(GL_POINTS)

        glColor4f(1.0, 0.55, 0.05, alpha)
        glVertex3f(0, 0, 0)

        glEnd()

    def draw_ambient(self):
        glPointSize(1.5)
        glBegin(GL_POINTS)

        for particle in self.ambient:
            particle[1] += particle[2]

            radius = particle[0]
            angle = particle[1]

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = math.sin(self.time + angle) * 0.25

            glColor4f(1.0, 0.65, 0.12, 0.55)
            glVertex3f(x, y, z)

        glEnd()

    def draw_spikes(self):
        glLineWidth(1.5)
        glBegin(GL_LINES)

        for i in range(18):
            angle = (
                i * 2 * math.pi / 18
                + self.time * 0.12
            )

            length = (
                2.05
                + math.sin(self.time * 3 + i) * 0.16
            )

            glColor4f(1.0, 0.45, 0.03, 0.55)
            glVertex3f(0, 0, 0)

            glColor4f(1.0, 0.15, 0.0, 0.0)

            glVertex3f(
                length * math.cos(angle),
                length * math.sin(angle),
                0
            )

        glEnd()

    def draw_rings(self):
        rings = [
            (1.25, 0.18, self.angle * 1.30, 0.55),
            (1.45, 0.30, -self.angle * 1.00, 0.48),
            (1.65, 0.22, self.angle * 0.80, 0.42),
            (1.85, 0.38, -self.angle * 0.60, 0.35),
            (2.05, 0.28, self.angle * 0.45, 0.28),
            (2.25, 0.45, -self.angle * 0.30, 0.22)
        ]

        for radius, height, rotation, alpha in rings:
            glPushMatrix()

            glRotatef(
                rotation,
                0.4,
                1.0,
                0.2
            )

            glLineWidth(5.0)
            glBegin(GL_LINE_LOOP)

            glColor4f(
                1.0,
                0.25,
                0.0,
                alpha * 0.10
            )

            for i in range(80):
                angle = 2 * math.pi * i / 80

                glVertex3f(
                    radius * math.cos(angle),
                    height * math.sin(angle),
                    0
                )

            glEnd()

            glLineWidth(1.5)
            glBegin(GL_LINE_LOOP)

            glColor4f(
                1.0,
                0.45,
                0.03,
                alpha
            )

            for i in range(80):
                angle = 2 * math.pi * i / 80

                glVertex3f(
                    radius * math.cos(angle),
                    height * math.sin(angle),
                    0
                )

            glEnd()
            glPopMatrix()

        for side in range(4):
            start = (
                self.time * (0.8 + side * 0.15)
                + side * math.pi / 2
            )

            glLineWidth(3.0)
            glBegin(GL_LINE_STRIP)

            for i in range(30):
                angle = (
                    start
                    + i / 29 * math.pi / 2.5
                )

                radius = 2.10

                glColor4f(1.0, 0.50, 0.05, 0.70)

                glVertex3f(
                    radius * math.cos(angle),
                    radius * 0.45 * math.sin(angle),
                    math.sin(angle * 2) * 0.08
                )

            glEnd()

        glPointSize(5.0)
        glBegin(GL_POINTS)

        for i in range(8):
            angle = (
                self.time * 1.5
                + i * math.pi / 4
            )

            radius = 1.95

            glColor4f(1.0, 0.65, 0.08, 0.9)

            glVertex3f(
                radius * math.cos(angle),
                radius * 0.45 * math.sin(angle),
                0
            )

        glEnd()

    def draw_beams(self):
        glLineWidth(1.2)
        glBegin(GL_LINES)

        for i, beam in enumerate(self.beams):
            if i % 2 == 0:
                glColor4f(1.0, 0.50, 0.05, 0.65)
                glVertex3f(0, 0, 0)

                glColor4f(1.0, 0.20, 0.0, 0.0)
                glVertex3fv(beam)

        glEnd()

    def animate(self):
        self.angle += 0.45
        self.time += 0.02
        self.update()


# message input area and enter key bind
class MessageInput(QLineEdit):

    sendPressed = Signal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.sendPressed.emit()
            return

        super().keyPressEvent(event)


# the chat with translucent overlay
class ChatOverlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.setStyleSheet("""
            ChatOverlay {
                background-color: rgba(18, 10, 5, 235);
                border: none;
            }
        """)

        # scrolling area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: rgba(20, 10, 5, 90);
                width: 7px;
                margin: 3px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 130, 30, 150);
                border-radius: 3px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(255, 160, 50, 220);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet(
            "QWidget { background: transparent; border: none; }"
        )

        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(
            30, 25, 30, 25
        )

        self.chat_layout.setSpacing(12)
        self.chat_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.chat_widget)

        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.addWidget(self.scroll_area)

        self.processing_label = None
        self.processing_row = None
        self.processing_timer = None
        self.processing_dots = 0

    def create_bubble(self, text, is_user):
        bubble = QLabel(text)

        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.NoTextInteraction)

        viewport_width = self.scroll_area.viewport().width()

        if viewport_width <= 0:
            viewport_width = 760

        bubble.setMaximumWidth(
            min(
                500,
                max(260, viewport_width - 90)
            )
        )

        bubble.setMinimumWidth(0)
        bubble.setSizePolicy(
            QSizePolicy.Maximum,
            QSizePolicy.Preferred
        )

        if is_user:
            bubble.setStyleSheet("""
                QLabel {
                    color: #fff0d0;
                    background-color: rgba(255, 105, 15, 235);
                    border: 1px solid rgba(255, 180, 80, 190);
                    border-radius: 16px;
                    padding: 10px 14px;
                    font-size: 15px;
                    font-family: Arial;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    color: #ffad42;
                    background-color: rgba(28, 18, 8, 245);
                    border: 1px solid rgba(255, 130, 30, 120);
                    border-radius: 16px;
                    padding: 10px 14px;
                    font-size: 15px;
                    font-family: Arial;
                }
            """)

        bubble.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )

        bubble.adjustSize()
        return bubble

    def add_message_row(self, bubble, is_user):
        row = QWidget()
        row.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        if is_user:
            row_layout.addStretch()
            row_layout.addWidget(
                bubble,
                0,
                Qt.AlignRight
            )
        else:
            row_layout.addWidget(
                bubble,
                0,
                Qt.AlignLeft
            )
            row_layout.addStretch()

        self.chat_layout.addWidget(row)
        row.show()

        bubble.updateGeometry()
        row.updateGeometry()
        self.chat_layout.activate()
        self.chat_widget.adjustSize()

        QTimer.singleShot(
            0,
            self.scroll_to_bottom
        )

    def add_user_message(self, message):
        self.add_message_row(
            self.create_bubble(message, True),
            True
        )

    def add_ultron_message(self, message):
        self.add_message_row(
            self.create_bubble(message, False),
            False
        )

    def scroll_to_bottom(self):
        QTimer.singleShot(
            0,
            lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
        )

    # ultron processing start
    def start_ultron_response(self):
        if self.processing_timer:
            self.processing_timer.stop()

        if self.processing_row:
            self.processing_row.deleteLater()

        self.processing_dots = 0

        self.processing_label = QLabel("PROCESSING")

        self.processing_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 165, 60, 240);
                background: transparent;
                border: none;
                font-size: 14px;
                font-family: Consolas;
                padding: 4px 2px;
            }
        """)

        self.processing_row = QWidget()

        row_layout = QHBoxLayout(
            self.processing_row
        )

        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        row_layout.addWidget(
            self.processing_label
        )

        row_layout.addStretch()

        self.chat_layout.addWidget(
            self.processing_row
        )

        self.processing_timer = QTimer(self)
        self.processing_timer.timeout.connect(
            self.processing_tick
        )

        self.processing_timer.start(350)

        self.scroll_to_bottom()

    def processing_tick(self):
        if not self.processing_label:
            return

        self.processing_dots += 1

        if self.processing_dots > 3:
            self.processing_dots = 0

        self.processing_label.setText(
            "PROCESSING" + "." * self.processing_dots
        )

        self.scroll_to_bottom()

    def finish_processing(self, response):
        if self.processing_timer:
            self.processing_timer.stop()
            self.processing_timer = None

        if self.processing_row:
            self.chat_layout.removeWidget(
                self.processing_row
            )

            self.processing_row.deleteLater()
            self.processing_row = None
            self.processing_label = None

        self.add_ultron_message(response)


class UltronWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowFlag(
            Qt.FramelessWindowHint
        )

        self.setWindowTitle(
            "ULTRON"
        )

        self.resize(850, 550)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(
            20, 15, 20, 20
        )
        layout.setSpacing(2)

        # top bar
        top_bar = QWidget()

        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(5, 0, 5, 0)
        top_layout.setSpacing(0)

        title = QLabel("ULTRON")
        title.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        title.setFont(
            QFont("Arial", 30, QFont.Bold)
        )

        status = QLabel("● SYSTEM ONLINE")
        status.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        status.setFont(
            QFont("Arial", 13)
        )

        top_layout.addWidget(title, 1)
        top_layout.addWidget(status)

        # hologram
        core = HologramCore()

        # message area
        self.message_area = QWidget()

        message_layout = QHBoxLayout(
            self.message_area
        )

        message_layout.setContentsMargins(
            0, 8, 0, 0
        )
        message_layout.setSpacing(8)

        self.message_input = MessageInput()
        self.message_input.setPlaceholderText(
            "Send a message..."
        )
        self.message_input.setFixedHeight(46)

        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(20, 14, 10, 245);
                color: #fffaf0;
                border: 2px solid rgba(255, 135, 30, 190);
                border-radius: 12px;
                padding-left: 14px;
                padding-right: 14px;
                font-size: 15px;
            }

            QLineEdit:focus {
                border: 2px solid rgba(255, 170, 70, 230);
            }

            QLineEdit::placeholder {
                color: #d7a868;
            }
        """)

        send_button = QPushButton("➤")
        send_button.setFixedSize(46, 46)
        send_button.setToolTip("Send message")

        send_button.clicked.connect(
            self.send_message
        )

        self.message_input.sendPressed.connect(
            self.send_message
        )

        message_layout.addWidget(
            self.message_input,
            1
        )

        message_layout.addWidget(
            send_button
        )

        layout.addWidget(top_bar)
        layout.addWidget(core, 1)
        layout.addWidget(self.message_area)

        # chat overlay
        self.chat_overlay = ChatOverlay(central)
        self.chat_overlay.hide()

        central.setStyleSheet("""
            QWidget {
                background-color: rgb(18, 12, 8);
                color: #ff8c00;
            }

            QLabel {
                color: #ff8c00;
                background-color: transparent;
                border: none;
            }

            QPushButton {
                background-color: rgba(30, 18, 8, 230);
                color: #ff9d2e;
                border: 2px solid rgba(255, 120, 20, 180);
                border-radius: 12px;
                font-size: 22px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: rgba(60, 30, 10, 240);
            }

            QPushButton:pressed {
                background-color: rgba(255, 100, 10, 180);
            }
        """)

        QTimer.singleShot(
            0,
            self.update_overlay_geometry
        )

    def update_overlay_geometry(self):
        central = self.centralWidget()

        if central is None:
            return

        input_top = self.message_area.geometry().top()

        if input_top <= 0:
            return

        self.chat_overlay.setGeometry(
            0,
            0,
            central.width(),
            input_top
        )

        self.chat_overlay.raise_()
        self.message_area.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_overlay_geometry()

    # handle messages from the input box
    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        print("User:", message)

        self.message_input.clear()

        self.chat_overlay.show()
        self.update_overlay_geometry()

        self.chat_overlay.add_user_message(
            message
        )

        self.chat_overlay.start_ultron_response()

        QTimer.singleShot(
            3500,
            self.finish_fake_response
        )

    def finish_fake_response(self):
        self.chat_overlay.finish_processing(
            "Systems online. How may I assist you?"
        )


# start application
app = QApplication(sys.argv)

window = UltronWindow()
window.show()

QTimer.singleShot(
    0,
    window.update_overlay_geometry
)

sys.exit(app.exec())