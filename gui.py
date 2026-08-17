import sys
import math
import random

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QPropertyAnimation,
    QEasingCurve
)
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
    QTextEdit,
    QGraphicsOpacityEffect
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


# the core part with 3d renders and animations
class HologramCore(QOpenGLWidget):
    def __init__(self):
        super().__init__()

        # make the OpenGL area match the main window
        self.setAutoFillBackground(False)

        # rotating animation
        self.angle = 0
        self.time = 0

        # like sphere poly
        # smaller core
        self.vertices, self.edges = self.create_sphere(
            0.90,
            12,
            24
        )

        # energy beams
        self.beams = self.create_beams(
            24,
            2.25
        )

        # sphere particles
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

        # ambient particles
        self.ambient = []

        for _ in range(60):
            self.ambient.append([
                random.uniform(1.8, 2.6),
                random.uniform(0, 2 * math.pi),
                random.uniform(-0.004, 0.004)
            ])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)

        # slightly lower FPS so the PC doesn't work unnecessarily hard
        self.timer.start(20)


    # create the 3d sphere
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


    # energy beams
    def create_beams(self, count, length):

        beams = []

        for _ in range(count):

            theta = random.uniform(
                0,
                2 * math.pi
            )

            phi = random.uniform(
                0,
                math.pi
            )

            beams.append((
                length * math.sin(phi) * math.cos(theta),
                length * math.sin(phi) * math.sin(theta),
                length * math.cos(phi)
            ))

        return beams


    # colors blending and smoothness
    def initializeGL(self):

        glClearColor(
            0.070,
            0.047,
            0.031,
            1.0
        )

        glEnable(GL_BLEND)

        glBlendFunc(
            GL_SRC_ALPHA,
            GL_ONE
        )

        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

        glHint(
            GL_LINE_SMOOTH_HINT,
            GL_NICEST
        )

        glHint(
            GL_POINT_SMOOTH_HINT,
            GL_NICEST
        )


    def resizeGL(self, width, height):

        if height <= 0:
            height = 1

        glViewport(
            0,
            0,
            width,
            height
        )

        glMatrixMode(
            GL_PROJECTION
        )

        glLoadIdentity()

        gluPerspective(
            45.0,
            width / height,
            0.1,
            50.0
        )

        glMatrixMode(
            GL_MODELVIEW
        )


    # hologram core area
    def paintGL(self):

        glClear(
            GL_COLOR_BUFFER_BIT
        )

        glMatrixMode(
            GL_MODELVIEW
        )

        glLoadIdentity()

        # move the hologram back
        glTranslatef(
            0,
            0,
            -6
        )

        # energy effects don't need depth
        glDisable(
            GL_DEPTH_TEST
        )


        # background particles
        self.draw_ambient()


        # energy spikes
        self.draw_spikes()


        # main sphere
        glPushMatrix()

        glRotatef(
            self.angle,
            0.35,
            1.0,
            0.15
        )


        # glowing core
        # bigger center dot
        self.glow(95, 0.018)
        self.glow(65, 0.045)
        self.glow(42, 0.12)
        self.glow(25, 0.30)
        self.glow(17, 1.0)


        # wireframe sphere
        glLineWidth(1.0)

        glBegin(GL_LINES)

        for a, b in self.edges:

            glColor4f(
                1.0,
                0.42,
                0.03,
                0.75
            )

            glVertex3fv(
                self.vertices[a]
            )

            glVertex3fv(
                self.vertices[b]
            )

        glEnd()


        # sphere nodes
        glPointSize(2.0)

        glBegin(GL_POINTS)

        glColor4f(
            1.0,
            0.65,
            0.12,
            0.85
        )

        for vertex in self.vertices:
            glVertex3fv(vertex)

        glEnd()

        glPopMatrix()


        # outer particles
        glPushMatrix()

        glRotatef(
            -self.angle * 0.35,
            0.2,
            1.0,
            0.4
        )

        glPointSize(2.0)

        glBegin(GL_POINTS)

        glColor4f(
            1.0,
            0.50,
            0.05,
            0.55
        )

        for particle in self.particles:
            glVertex3fv(particle)

        glEnd()

        glPopMatrix()


        # lots of orange spinning rings
        self.draw_rings()


        # radial beams
        self.draw_beams()


        # turn depth testing back on
        glEnable(
            GL_DEPTH_TEST
        )


    # glowing center
    def glow(self, size, alpha):

        glPointSize(size)

        glBegin(GL_POINTS)

        glColor4f(
            1.0,
            0.55,
            0.05,
            alpha
        )

        glVertex3f(
            0,
            0,
            0
        )

        glEnd()


    # ambient space particles
    def draw_ambient(self):

        glPointSize(1.5)

        glBegin(GL_POINTS)

        for particle in self.ambient:

            particle[1] += particle[2]

            radius = particle[0]
            angle = particle[1]

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            z = math.sin(
                self.time + angle
            ) * 0.25

            glColor4f(
                1.0,
                0.65,
                0.12,
                0.55
            )

            glVertex3f(
                x,
                y,
                z
            )

        glEnd()


    # energy spikes
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
                + math.sin(
                    self.time * 3 + i
                ) * 0.16
            )

            # bright start
            glColor4f(
                1.0,
                0.45,
                0.03,
                0.55
            )

            glVertex3f(
                0,
                0,
                0
            )

            # fade out
            glColor4f(
                1.0,
                0.15,
                0.0,
                0.0
            )

            glVertex3f(
                length * math.cos(angle),
                length * math.sin(angle),
                0
            )

        glEnd()


    # orange orbital rings
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


            # soft glow around ring
            glLineWidth(5.0)

            glBegin(GL_LINE_LOOP)

            glColor4f(
                1.0,
                0.25,
                0.0,
                alpha * 0.10
            )

            for i in range(80):

                angle = (
                    2 * math.pi * i / 80
                )

                glVertex3f(
                    radius * math.cos(angle),
                    height * math.sin(angle),
                    0
                )

            glEnd()


            # bright ring
            glLineWidth(1.5)

            glBegin(GL_LINE_LOOP)

            glColor4f(
                1.0,
                0.45,
                0.03,
                alpha
            )

            for i in range(80):

                angle = (
                    2 * math.pi * i / 80
                )

                glVertex3f(
                    radius * math.cos(angle),
                    height * math.sin(angle),
                    0
                )

            glEnd()

            glPopMatrix()


        # rotating broken arcs
        for side in range(4):

            start = (
                self.time *
                (0.8 + side * 0.15)
                + side * math.pi / 2
            )

            glLineWidth(3.0)

            glBegin(GL_LINE_STRIP)

            for i in range(30):

                angle = (
                    start +
                    i / 29 *
                    math.pi / 2.5
                )

                radius = 2.10

                glColor4f(
                    1.0,
                    0.50,
                    0.05,
                    0.70
                )

                glVertex3f(
                    radius * math.cos(angle),
                    radius * 0.45 * math.sin(angle),
                    math.sin(angle * 2) * 0.08
                )

            glEnd()


        # little rotating energy dots
        glPointSize(5.0)

        glBegin(GL_POINTS)

        for i in range(8):

            angle = (
                self.time * 1.5
                + i * math.pi / 4
            )

            radius = 1.95

            glColor4f(
                1.0,
                0.65,
                0.08,
                0.9
            )

            glVertex3f(
                radius * math.cos(angle),
                radius * 0.45 * math.sin(angle),
                0
            )

        glEnd()


    # radial energy beams
    def draw_beams(self):

        glLineWidth(1.2)

        glBegin(GL_LINES)

        for i, beam in enumerate(self.beams):

            if i % 2 == 0:

                # bright beam starting from core
                glColor4f(
                    1.0,
                    0.50,
                    0.05,
                    0.65
                )

                glVertex3f(
                    0,
                    0,
                    0
                )

                # fade toward outside
                glColor4f(
                    1.0,
                    0.20,
                    0.0,
                    0.0
                )

                glVertex3fv(
                    beam
                )

        glEnd()


    def animate(self):

        # smooth continuous animation
        self.angle += 0.45

        self.time += 0.02

        self.update()


# message input area and enter key bind
class MessageInput(QLineEdit):

    sendPressed = Signal()

    def keyPressEvent(self, event):

        if event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter
        ):

            self.sendPressed.emit()

            return

        super().keyPressEvent(event)

#the chat wit translucent overlay
class ChatOverlay(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 100, 10, 50);
                border: 1px solid rgba(255, 150, 50, 130);
            }
        """)
        # fade anim
        self.opacity_effect = QGraphicsOpacityEffect(
            self
        )

        self.setGraphicsEffect(
            self.opacity_effect
        )

        self.fade_animation = QPropertyAnimation(
            self.opacity_effect,
            b"opacity"
        )

        self.fade_animation.setDuration(
            450
        )

        self.fade_animation.setStartValue(
            0.0
        )

        self.fade_animation.setEndValue(
            1.0
        )

        self.fade_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )


    # chat fade in
    def showEvent(self, event):

        self.opacity_effect.setOpacity(
            0.0
        )

        self.fade_animation.stop()
        self.fade_animation.start()

        super().showEvent(
            event
        )
# main window with everything
class UltronWindow(QMainWindow):

    def __init__(self):
        super().__init__()


        self.setWindowFlag(
            Qt.FramelessWindowHint
        )

        self.setWindowTitle(
            "ULTRON"
        )

        # original bigger window
        self.resize(
            850,
            550
        )


        central = QWidget()

        self.setCentralWidget(
            central
        )


        layout = QVBoxLayout(
            central
        )

        layout.setContentsMargins(
            20,
            15,
            20,
            20
        )

        layout.setSpacing(2)

        #top bar
        top_bar = QWidget()

        top_layout = QHBoxLayout(
            top_bar
        )

        top_layout.setContentsMargins(
            5,
            0,
            5,
            0
        )

        top_layout.setSpacing(0)


        # title
        title = QLabel(
            "ULTRON"
        )

        title.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )

        title.setFont(
            QFont(
                "Arial",
                30,
                QFont.Bold
            )
        )


        # system status
        status = QLabel(
            "● SYSTEM ONLINE"
        )

        status.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        status.setFont(
            QFont(
                "Arial",
                13
            )
        )



        top_layout.addWidget(
            title,
            1
        )

        top_layout.addWidget(
            status
        )

        # hologram
        core = HologramCore()
        #chatting overlay that will cover hologream
        

        # message area
        message_area = QWidget()

        message_layout = QHBoxLayout(
            message_area
        )

        message_layout.setContentsMargins(
            0,
            8,
            0,
            0
        )

        message_layout.setSpacing(8)


        # input area
        self.message_input = MessageInput()

        self.message_input.setPlaceholderText(
            "Send a message..."
        )

        self.message_input.setFixedHeight(
            46
        )


        # send btn
        send_button = QPushButton(
            "➤"
        )

        send_button.setFixedSize(
            46,
            46
        )

        send_button.setToolTip(
            "Send message"
        )


        # send the message when clicked
        send_button.clicked.connect(
            self.send_message
        )

        # send the message when Enter is pressed
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


        layout.addWidget(
            top_bar
        )

        layout.addWidget(
            core,
            1
        )

        layout.addWidget(
            message_area
        )

        #chat over will cover all area

        self.chat_overlay = ChatOverlay(
            central
        )

        self.chat_overlay.setGeometry(
            central.rect()
        )

        self.chat_overlay.hide()


        #voerlay is above all things
        self.chat_overlay.raise_()

        
        # translucent hologram-style background
        # dark holographic glass background
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

            QLineEdit {
                background-color: rgba(10, 7, 5, 220);
                color: #ff9d2e;
                border: 2px solid rgba(255, 120, 20, 170);
                border-radius: 12px;
                padding-left: 14px;
                padding-right: 14px;
                font-size: 15px;
            }

            QLineEdit:focus {
                border: 2px solid rgba(255, 150, 40, 220);
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

    def resizeEvent(self, event):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "chat_overlay"
        ):

            self.chat_overlay.setGeometry(
                self.centralWidget().rect()
            )
    # handle messages from the input box
    def send_message(self):

        message = self.message_input.text().strip()

        if not message:
            return

        print(
            "User:",
            message
        )

        self.message_input.clear()

        self.chat_overlay.show()


# start application
app = QApplication(
    sys.argv
)

window = UltronWindow()

window.show()

sys.exit(
    app.exec()
)