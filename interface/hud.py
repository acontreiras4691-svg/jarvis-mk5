import math
import random
import psutil

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QRadialGradient
from PyQt6.QtCore import Qt, QTimer


class JarvisHUD(QWidget):

    def __init__(self, audio_manager):
        super().__init__()

        self.audio_manager = audio_manager

        # posição ideal para 2560x1440
        self.setGeometry(430, 180, 1700, 1000)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.estado = "IDLE"
        self.texto = "Jarvis online."

        self.rot1 = 0
        self.rot2 = 0
        self.rot3 = 0
        self.rot4 = 0

        self.audio_level = 0
        self.expansao = 0

        # olhos
        self.blink_timer = 0
        self.blink_state = 1

        # partículas
        self.particles = []

        for _ in range(100):
            self.particles.append([
                random.uniform(-350, 350),
                random.uniform(-350, 350),
                random.uniform(0.5, 1.5)
            ])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    # -------------------------

    def set_estado(self, estado):
        self.estado = estado

    def set_texto(self, texto):
        self.texto = texto

    # -------------------------

    def update_frame(self):

        self.rot1 += 0.6
        self.rot2 -= 1.2
        self.rot3 += 1.8
        self.rot4 += 3

        # nível de áudio
        try:
            level = self.audio_manager.get_audio_level()
        except:
            level = 0

        self.audio_level = self.audio_level * 0.85 + level * 0.15

        # expansão quando fala
        if self.estado == "RESPONDENDO":
            self.expansao = self.expansao * 0.9 + 1 * 0.1
        else:
            self.expansao = self.expansao * 0.9

        # piscar olhos
        self.blink_timer += 1

        if self.blink_timer > 180:
            self.blink_state = 0

        if self.blink_timer > 195:
            self.blink_state = 1
            self.blink_timer = 0

        self.update()

    # -------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = int(self.width() / 2)
        cy = int(self.height() / 2)

        base_radius = 150

        radius = int(base_radius + self.audio_level * 100 + self.expansao * 60)

        azul = QColor(0, 200, 255)
        laranja = QColor(255, 170, 0)

        cor = azul

        if self.estado == "PROCESSANDO":
            cor = laranja

        if self.estado == "RESPONDENDO":
            cor = QColor(0, 255, 180)

        # -------------------------
        # GLOW
        # -------------------------

        glow = QRadialGradient(cx, cy, radius + 300)

        glow.setColorAt(0, QColor(cor.red(), cor.green(), cor.blue(), 120))
        glow.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            int(cx - radius - 120),
            int(cy - radius - 120),
            int((radius + 120) * 2),
            int((radius + 120) * 2)
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

            if p[1] < -450:
                p[1] = 450

            painter.drawPoint(int(p[0]), int(p[1]))

        painter.restore()

        # -------------------------
        # ANEL EXTERIOR
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot1)

        pen = QPen(azul)
        pen.setWidth(3)
        painter.setPen(pen)

        r = radius + 90

        for i in range(40):

            ang = math.radians(i * 9)

            x1 = math.cos(ang) * r
            y1 = math.sin(ang) * r

            x2 = math.cos(ang) * (r + 14)
            y2 = math.sin(ang) * (r + 14)

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.restore()

        # -------------------------
        # ANEL MÉDIO
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot2)

        pen2 = QPen(QColor(0, 220, 255))
        pen2.setWidth(2)
        painter.setPen(pen2)

        mid = radius + 40

        painter.drawEllipse(
            int(-mid),
            int(-mid),
            int(mid * 2),
            int(mid * 2)
        )

        painter.restore()

        # -------------------------
        # RADAR
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot4)

        radar_pen = QPen(QColor(0, 255, 255, 160))
        radar_pen.setWidth(3)
        painter.setPen(radar_pen)

        painter.drawLine(0, 0, int(radius + 120), 0)

        painter.restore()

        # -------------------------
        # ANEL INTERNO
        # -------------------------

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rot3)

        pen3 = QPen(QColor(0, 255, 200))
        pen3.setWidth(3)
        painter.setPen(pen3)

        inner = radius - 60

        painter.drawEllipse(
            int(-inner),
            int(-inner),
            int(inner * 2),
            int(inner * 2)
        )

        painter.restore()

        # -------------------------
        # ARC REACTOR
        # -------------------------

        core_radius = 60

        core = QRadialGradient(cx, cy, core_radius)
        core.setColorAt(0, QColor(255, 200, 100))
        core.setColorAt(1, QColor(255, 120, 0))

        painter.setBrush(core)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            int(cx - core_radius),
            int(cy - core_radius),
            int(core_radius * 2),
            int(core_radius * 2)
        )

        # -------------------------
        # AVATAR
        # -------------------------

        painter.setPen(QPen(QColor(0, 255, 255), 5))

        olho_offset = 50

        eye_height = 16 if self.blink_state else 2

        painter.drawEllipse(int(cx - olho_offset - 8), int(cy - 20), 16, eye_height)
        painter.drawEllipse(int(cx + olho_offset - 8), int(cy - 20), 16, eye_height)

        painter.drawLine(int(cx - 18), int(cy + 35), int(cx + 18), int(cy + 35))

        # -------------------------
        # ONDAS DE VOZ
        # -------------------------

        wave_pen = QPen(QColor(255, 170, 0, 140))
        wave_pen.setWidth(2)
        painter.setPen(wave_pen)

        for i in range(3):

            r = radius + 150 + i * 40 + self.audio_level * 100

            painter.drawEllipse(
                int(cx - r),
                int(cy - r),
                int(r * 2),
                int(r * 2)
            )

        # -------------------------
        # TEXTO
        # -------------------------

        painter.setPen(QColor(220, 255, 255))
        painter.setFont(QFont("Orbitron", 18))

        painter.drawText(
            self.rect().adjusted(300, 240, -300, -240),
            Qt.AlignmentFlag.AlignCenter |
            Qt.TextFlag.TextWordWrap,
            self.texto
        )

        # -------------------------
        # PAINEL ESQUERDO
        # -------------------------

        painter.setFont(QFont("Consolas", 12))
        painter.setPen(QColor(0, 255, 255))

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        painter.drawText(40, 120, f"CPU: {cpu}%")
        painter.drawText(40, 150, f"RAM: {ram}%")
        painter.drawText(40, 180, f"STATE: {self.estado}")

        # -------------------------
        # PAINEL DIREITO
        # -------------------------

        painter.drawText(self.width() - 260, 120, "JARVIS AI")
        painter.drawText(self.width() - 260, 150, "Neural Core: ONLINE")
        painter.drawText(self.width() - 260, 180, "Voice Engine: ACTIVE")


def iniciar_hud(audio_manager):
    return JarvisHUD(audio_manager)