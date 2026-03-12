import math
import random
import psutil
import time

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QRadialGradient
from PyQt6.QtCore import Qt, QTimer


class JarvisHUD(QWidget):

    def __init__(self, audio_manager):
        super().__init__()

        self.audio_manager = audio_manager

        # FULLSCREEN
        self.showFullScreen()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.estado = "IDLE"
        self.texto = "Jarvis online."

        # animações
        self.rot1 = 0
        self.rot2 = 0
        self.rot3 = 0
        self.rot4 = 0

        self.audio_level = 0

        # rede
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()
        self.net_down = 0
        self.net_up = 0

        # partículas
        self.particles = []
        for _ in range(150):
            self.particles.append([
                random.uniform(-700, 700),
                random.uniform(-700, 700),
                random.uniform(0.3, 1.5)
            ])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    # ---------------------------------

    def set_estado(self, estado):
        self.estado = estado

    def set_texto(self, texto):
        self.texto = texto

    # ---------------------------------

    def update_network(self):

        now = time.time()
        net = psutil.net_io_counters()

        dt = now - self.last_time

        if dt <= 0:
            return

        self.net_down = (net.bytes_recv - self.last_net.bytes_recv) / dt / 1024
        self.net_up = (net.bytes_sent - self.last_net.bytes_sent) / dt / 1024

        self.last_net = net
        self.last_time = now

    # ---------------------------------

    def update_frame(self):

        self.rot1 += 0.4
        self.rot2 -= 1.0
        self.rot3 += 1.3
        self.rot4 += 3

        try:
            level = self.audio_manager.get_audio_level()
        except:
            level = 0

        self.audio_level = self.audio_level * 0.85 + level * 0.15

        self.update_network()

        self.update()

    # ---------------------------------

    def draw_bar(self, painter, x, y, width, percent):

        fill = int(width * percent / 100)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor(0, 230, 255, 200))
        painter.drawRect(x, y, fill, 12)

        painter.setBrush(QColor(0, 80, 100, 120))
        painter.drawRect(x + fill, y, width - fill, 12)

    # ---------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = int(self.width() / 2)
        cy = int(self.height() / 2)

        radius = 220 + int(self.audio_level * 150)

        azul = QColor(0, 230, 255)
        laranja = QColor(255, 170, 0)

        cor = azul

        if self.estado == "PROCESSANDO":
            cor = laranja

        if self.estado == "RESPONDENDO":
            cor = QColor(0, 255, 180)

        # -------------------------
        # GLOW
        # -------------------------

        glow = QRadialGradient(cx, cy, radius + 500)

        glow.setColorAt(0, QColor(cor.red(), cor.green(), cor.blue(), 120))
        glow.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            cx - radius - 300,
            cy - radius - 300,
            (radius + 300) * 2,
            (radius + 300) * 2
        )

        # -------------------------
        # PARTICULAS
        # -------------------------

        painter.save()
        painter.translate(cx, cy)

        pen = QPen(QColor(0, 255, 255, 120))
        pen.setWidth(2)

        painter.setPen(pen)

        for p in self.particles:

            p[1] -= p[2]

            if p[1] < -900:
                p[1] = 900

            painter.drawPoint(int(p[0]), int(p[1]))

        painter.restore()

        # -------------------------
        # ANEL EXTERIOR
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot1)

        pen = QPen(QColor(0, 220, 255))
        pen.setWidth(3)

        painter.setPen(pen)

        r = radius + 160

        for i in range(80):

            ang = math.radians(i * 4.5)

            x1 = math.cos(ang) * r
            y1 = math.sin(ang) * r

            x2 = math.cos(ang) * (r + 20)
            y2 = math.sin(ang) * (r + 20)

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.restore()

        # -------------------------
        # ANEL MÉDIO
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot2)

        pen = QPen(QColor(0, 255, 220))
        pen.setWidth(2)

        painter.setPen(pen)

        mid = radius + 90

        painter.drawEllipse(-mid, -mid, mid * 2, mid * 2)

        painter.restore()

        # -------------------------
        # RADAR
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot4)

        radar_pen = QPen(QColor(0, 255, 255, 200))
        radar_pen.setWidth(3)

        painter.setPen(radar_pen)

        painter.drawLine(0, 0, radius + 200, 0)

        painter.restore()

        # -------------------------
        # CORE
        # -------------------------

        core_r = 100

        core = QRadialGradient(cx, cy, core_r)

        core.setColorAt(0, QColor(255, 230, 140))
        core.setColorAt(1, QColor(255, 120, 0))

        painter.setBrush(core)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(cx - core_r, cy - core_r, core_r * 2, core_r * 2)

        # -------------------------
        # TEXTO CENTRAL
        # -------------------------

        painter.setPen(QColor(220, 255, 255))
        painter.setFont(QFont("Orbitron", 24))

        painter.drawText(
            self.rect().adjusted(400, 300, -400, -300),
            Qt.AlignmentFlag.AlignCenter |
            Qt.TextFlag.TextWordWrap,
            self.texto
        )

        # -------------------------
        # PAINEL ESQUERDO
        # -------------------------

        painter.setFont(QFont("Consolas", 14))
        painter.setPen(QColor(0, 255, 255))

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        x = 80
        y = 160

        painter.drawText(x, y, "CPU")
        self.draw_bar(painter, x, y + 15, 220, cpu)

        painter.drawText(x, y + 60, "RAM")
        self.draw_bar(painter, x, y + 75, 220, ram)

        painter.drawText(x, y + 140, f"STATE: {self.estado}")

        # -------------------------
        # PAINEL DIREITO
        # -------------------------

        rx = self.width() - 380

        painter.drawText(rx, 160, "JARVIS AI")
        painter.drawText(rx, 200, "Neural Core: ONLINE")
        painter.drawText(rx, 230, "Voice Engine: ACTIVE")

        painter.drawText(rx, 300, f"NET ↓ {self.net_down:.1f} KB/s")
        painter.drawText(rx, 330, f"NET ↑ {self.net_up:.1f} KB/s")

        # -------------------------
        # VISUALIZADOR VOZ
        # -------------------------

        painter.setPen(QPen(QColor(255, 170, 0, 200), 4))

        base_y = cy + 350

        for i in range(60):

            h = random.randint(5, int(50 + self.audio_level * 200))

            x = cx - 600 + i * 20

            painter.drawLine(x, base_y, x, base_y - h)


def iniciar_hud(audio_manager):
    return JarvisHUD(audio_manager)