# ==================================================
# GESTOR DE CONVERSA - JARVIS MK5
# ==================================================

import time

from core.estado import EstadoJarvis
from config.configuracoes import TEMPO_TIMEOUT_CONVERSA
from core.logger import log


class GestorConversa:

    def __init__(self):

        self.estado = EstadoJarvis.IDLE
        self.ultima_interacao = time.time()

    # ==================================================
    # ATIVAR JARVIS
    # ==================================================

    def ativar(self):

        if self.estado != EstadoJarvis.ATIVO:

            log("Jarvis ativado.")

        self.estado = EstadoJarvis.ATIVO
        self.ultima_interacao = time.time()

    # ==================================================
    # REGISTAR INTERAÇÃO
    # ==================================================

    def atualizar_interacao(self):

        self.ultima_interacao = time.time()

    # ==================================================
    # VERIFICAR TIMEOUT
    # ==================================================

    def verificar_timeout(self):

        if self.estado != EstadoJarvis.ATIVO:
            return

        tempo_passado = time.time() - self.ultima_interacao

        if tempo_passado > TEMPO_TIMEOUT_CONVERSA:

            log("⏳ Timeout de conversa. Jarvis voltou para IDLE.")

            self.estado = EstadoJarvis.IDLE

    # ==================================================
    # TERMINAR CONVERSA
    # ==================================================

    def terminar(self):

        log("Jarvis voltou para modo IDLE.")

        self.estado = EstadoJarvis.IDLE