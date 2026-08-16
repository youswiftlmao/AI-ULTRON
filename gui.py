import sys
import math
import random

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
)

from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *

#the core part with 3d renders and animations
class HologramCore(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        #rotating animation
        self.angle = 0

        self.vertices, self.edges = self.create_sphere(
            1.5,
            12,
            24
        )
        
        self.beams = self.create_beams(
            20,
            2.8
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)



        #like sphere poly



    def create_sphere(self, radius, rings, segments):
        vertices = []
        edges = []

        for i in range(rings + 1):
            lat = math.pi * (i / rings - 0.5)

            sin_lat = math.sin(lat)
            cos_lat = math.cos(lat)

            for j in range(segments):
                lon = 2 * math.pi * j / segments

                sin_lon = math.sin(lon)
                cos_lon = math.cos(lon)

                x = radius * cos_lon * cos_lat

                y = radius * sin_lon * cos_lat


                z = radius * sin_lat

                vertices.append((x, y, z))

        for i in range(rings):
            for j in range(segments):
                p1 = i * segments + j
                p2 = p1 + segments
                p3 = i * segments + ((j + 1) % segments)

                edges.append((p1, p3))

                edges.append((p1, p2))

        return vertices, edges
    #energy beams
    def create_beams(self, num_beams, max_length):
        beams = []

        for _ in range(num_beams):
            theta = random.uniform(0, 2 * math.pi)

            phi = random.uniform(0, math.pi)

            x = math.sin(phi) * math.cos(theta) * max_length
            y = math.sin(phi) * math.sin(theta) * max_length
            z = math.cos(phi) * max_length

            beams.append((x, y, z))

        return beams

    
    #colors blending and smoothness


    def initializeGL(self):
        glClearColor(
            0.015,
            0.008,
            0.003,
            1.0
        )



        glEnable(GL_BLEND)

        glBlendFunc(
            GL_SRC_ALPHA,
            GL_ONE
        )

        glEnable(GL_POINT_SMOOTH)

        glEnable(GL_LINE_SMOOTH)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1


        glViewport(
            0,
            0,
            width,
            height
        )

        glMatrixMode(GL_PROJECTION)

        glLoadIdentity()


        gluPerspective(
            45,
            width / height,
            0.1,
            50.0
        )



        glMatrixMode(GL_MODELVIEW)
    #hologram core area 



    def paintGL(self):
        glClear(
            GL_COLOR_BUFFER_BIT |
            GL_DEPTH_BUFFER_BIT

        )

        glLoadIdentity()



        glTranslatef(
            0.0,
            0.0,
            -6.0
        )


        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE)


        glPushMatrix()

        glRotatef(
            self.angle,
            0.35,
            1,0,
            0.15
        )


        glPointSize(4.0)

        glBegin(GL_POINTS)

        glColor4f(
            1.0,
            0.95,
            0.55,
            1.0

        )



        glVertex3f(
            0.0,
            0.0,
            0.0
        )

        glEnd()
        glLineWidth(1.2)


        glBegin(GL_LINES)

        for edge in self.edges:
            for vertex in edge:
                glColor4f(
                    1.0,
                    0.45,
                    0.05,
                    0.75
                )


                glVertex3fv(
                    self.vertices[vertex]
                )

        glEnd()

        glPointSize(2.5)


        glBegin(GL_POINTS)

        for vertex in self.vertices:













    def animate(self):
        self.angle += 0.5

        if self.angle >= 360:
            self.angle = 0

        self.update()

    #main window eith everything
class UltronWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowFlag(
            Qt.FramelessWindowHint
        )

        self.setWindowTitle("ULTRON")
        self.resize(850, 550)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        central.setLayout(layout)

        title = QLabel("ULTRON")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(
            QFont(
                "Arial",
                36,
                QFont.Bold
            )
        )

        status = QLabel("● SYSTEM ONLINE")
        status.setAlignment(Qt.AlignCenter)
        status.setFont(
            QFont(
                "Arial",
                16
            )
        )

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